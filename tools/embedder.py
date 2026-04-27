import os
from typing import List, Any

from dotenv import load_dotenv
from google import genai
from langchain_chroma import Chroma
from langchain_core.documents import Document

from pipeline.schemas import Chunk


PERSIST_DIR = "./data/vector_db"
COLLECTION_NAME = "embeddings"


class VertexEmbeddingFunction:
    """
    Embedding function that uses Google Vertex AI through ADC.
    This uses the Google Cloud project shared with you by your friend.
    """

    def __init__(self):
        load_dotenv()

        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")


        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT is missing in .env")

        self.client = genai.Client(
            vertexai=True,
            project=self.project_id,
            location=self.location,
        )

        self.model_name = "gemini-embedding-001"

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []

        for text in texts:
            response = self.client.models.embed_content(
                model=self.model_name,
                contents=text,
            )

            embeddings.append(response.embeddings[0].values)

        return embeddings

    def embed_query(self, text: str) -> List[float]:
        response = self.client.models.embed_content(
            model=self.model_name,
            contents=text,
        )

        return response.embeddings[0].values


class ChromaEmbedder:
    """
    Stores document chunks inside ChromaDB using Vertex AI embeddings.
    """

    def __init__(
        self,
        persist_dir: str = PERSIST_DIR,
        collection_name: str = COLLECTION_NAME,
    ):
        self.embeddings = VertexEmbeddingFunction()

        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=persist_dir,
            collection_metadata={"hnsw:space": "cosine"},
        )

    def clean_metadata(self, metadata: dict) -> dict:
        """
        ChromaDB does not like None values in metadata.
        This converts None values to empty strings.
        """
        clean = {}

        for key, value in metadata.items():
            if value is None:
                clean[key] = ""
            elif isinstance(value, (str, int, float, bool)):
                clean[key] = value
            else:
                clean[key] = str(value)

        return clean

    def chunks_to_documents(self, chunks: List[Chunk]) -> List[Document]:
        documents = []

        for chunk in chunks:
            metadata = dict(chunk.metadata)

            metadata["chunk_id"] = chunk.chunk_id
            metadata["source_file"] = chunk.source_file
            metadata["filename"] = chunk.source_file
            metadata["page"] = chunk.page_number

            documents.append(
                Document(
                    page_content=chunk.text,
                    metadata=self.clean_metadata(metadata),
                )
            )

        return documents

    def add_chunks(self, chunks: List[Chunk]) -> None:
        if not chunks:
            print("No chunks to store.")
            return

        documents = self.chunks_to_documents(chunks)
        ids = [chunk.chunk_id for chunk in chunks]

        self.vector_store.add_documents(
            documents=documents,
            ids=ids,
        )

        print(f"Stored {len(chunks)} chunks in ChromaDB.")

    def search(self, query: str, k: int = 5, filter: dict = None) -> List[Any]:
        """
        Search for documents, optionally filtering by metadata (like student_id).
        """
        return self.vector_store.similarity_search(query=query, k=k, filter=filter)