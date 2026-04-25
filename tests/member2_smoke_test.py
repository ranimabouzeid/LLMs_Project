import os
import sys
from pathlib import Path

# Ensure root is in path
sys.path.append(os.getcwd())

from tools.document_loader import load_document
from tools.chunker import chunk_loaded_pages
from tools.embedder import ChromaEmbedder

def run_smoke_test():
    pdf_path = "data/uploads/L8- LSTM and GRU.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: {pdf_path} not found!")
        return

    print(f"📄 [1/4] Loading document: {pdf_path}...")
    try:
        pages = load_document(pdf_path)
        print(f"   ✅ Loaded {len(pages)} pages.")
    except Exception as e:
        print(f"   ❌ Loading failed: {e}")
        return

    print("\n✂️ [2/4] Chunking pages...")
    try:
        chunks = chunk_loaded_pages(pages)
        print(f"   ✅ Created {len(chunks)} chunks.")
    except Exception as e:
        print(f"   ❌ Chunking failed: {e}")
        return

    print("\n📦 [3/4] Indexing in ChromaDB (using Vertex AI)...")
    try:
        embedder = ChromaEmbedder()
        embedder.add_chunks(chunks)
        print("   ✅ Indexing complete.")
    except Exception as e:
        print(f"   ❌ Indexing failed: {e}")
        return

    print("\n🔍 [4/4] Testing Search Query: 'What is the vanishing gradient problem?'")
    try:
        results = embedder.search("What is the vanishing gradient problem?", k=2)
        print(f"   ✅ Found {len(results)} results.")
        for i, res in enumerate(results):
            print(f"\n--- Result {i+1} ---")
            print(f"Source: {res.metadata.get('source_file')}, Page: {res.metadata.get('page')}")
            print(f"Text: {res.page_content[:200]}...")
    except Exception as e:
        print(f"   ❌ Search failed: {e}")

if __name__ == "__main__":
    run_smoke_test()
