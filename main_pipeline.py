import os
from typing import List, Dict, Any

from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings


API_KEY = os.environ.get("GOOGLE_API_KEY")
PERSIST_DIR = "./data/vector_db"
COLLECTION_NAME = "embeddings"


class Retriever:
    def __init__(self, persist_dir: str, api_key: str):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001",
            google_api_key=api_key
        )

        self.vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=persist_dir,
            collection_metadata={"hnsw:space": "cosine"}
        )

    def retrieve(self, query: str, k: int = 8):
        return self.vector_store.similarity_search(query=query, k=k)


class EvidenceAwareSelector:
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm

    def score_chunk(self, query: str, chunk_text: str) -> Dict[str, float]:
        prompt = f"""
You are evaluating a study source chunk for tutoring quality.

Student question:
{query}

Chunk:
{chunk_text}

Score the chunk from 1 to 5 on:
1. EvidenceQuality = how clear, specific, and informative the chunk is
2. EducationalUsefulness = how useful the chunk is for deep understanding and teaching

Return exactly in this format:
EvidenceQuality: X
EducationalUsefulness: Y
"""

        try:
            response = self.llm.invoke(prompt).content.strip()
        except Exception:
            return {
                "evidence_quality": 3.0,
                "educational_usefulness": 3.0
            }

        eq = 3.0
        eu = 3.0

        for line in response.splitlines():
            line = line.strip()
            if line.startswith("EvidenceQuality:"):
                try:
                    eq = float(line.split(":", 1)[1].strip())
                except ValueError:
                    eq = 3.0
            elif line.startswith("EducationalUsefulness:"):
                try:
                    eu = float(line.split(":", 1)[1].strip())
                except ValueError:
                    eu = 3.0

        return {
            "evidence_quality": eq,
            "educational_usefulness": eu
        }

    def rerank(self, query: str, docs: List[Any]) -> List[Dict[str, Any]]:
        scored_docs = []

        for rank, doc in enumerate(docs):
            chunk_text = doc.page_content[:1500]
            scores = self.score_chunk(query, chunk_text)

            relevance_score = max(1.0, 5.0 - (rank * 0.5))

            final_score = (
                0.45 * relevance_score +
                0.25 * scores["evidence_quality"] +
                0.30 * scores["educational_usefulness"]
            )

            scored_docs.append({
                "doc": doc,
                "relevance_score": relevance_score,
                "evidence_quality": scores["evidence_quality"],
                "educational_usefulness": scores["educational_usefulness"],
                "final_score": final_score
            })

        scored_docs.sort(key=lambda x: x["final_score"], reverse=True)
        return scored_docs


def build_context(selected_docs: List[Dict[str, Any]], max_chunks: int = 4) -> str:
    context_parts = []

    for item in selected_docs[:max_chunks]:
        doc = item["doc"]
        source = doc.metadata.get("filename", "Unknown")
        page = doc.metadata.get("page", "Unknown")

        context_parts.append(
            f"[Source: {source}, Page: {page}]\n{doc.page_content}"
        )

    return "\n\n".join(context_parts)


def generate_study_response(llm: ChatGoogleGenerativeAI, query: str, context: str) -> str:
    prompt = f"""
You are DeepStudy Coach, an educational AI tutor.

Your goal is to help the student understand, not memorize.
Do not give only a shallow definition.
Use ONLY the source material below.

Answer in this structure:

1. Core Explanation
2. Key Ideas
3. What Students Commonly Miss
4. Concept Connections
5. 3 MCQs
6. 1 Challenge Question

Student question:
{query}

Source material:
{context}
"""
    return llm.invoke(prompt).content


def check_coverage(llm: ChatGoogleGenerativeAI, query: str, context: str, answer: str) -> str:
    prompt = f"""
You are checking concept coverage.

Student question:
{query}

Source material:
{context}

Generated answer:
{answer}

Return:
1. Covered concepts
2. Missing or weakly covered concepts
3. What to review next

Keep it concise and student-friendly.
"""
    return llm.invoke(prompt).content


def create_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=API_KEY,
        temperature=0.2
    )


def run_pipeline(user_query: str) -> Dict[str, Any]:
    if not API_KEY:
        raise ValueError("GOOGLE_API_KEY is missing.")

    llm = create_llm()
    retriever = Retriever(PERSIST_DIR, API_KEY)
    selector = EvidenceAwareSelector(llm)

    retrieved_docs = retriever.retrieve(user_query, k=8)
    ranked_docs = selector.rerank(user_query, retrieved_docs)
    context = build_context(ranked_docs, max_chunks=4)

    answer = generate_study_response(llm, user_query, context)
    coverage = check_coverage(llm, user_query, context, answer)

    return {
        "ranked_docs": ranked_docs,
        "context": context,
        "answer": answer,
        "coverage": coverage
    }
