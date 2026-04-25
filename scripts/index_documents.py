import os
import sys
from pathlib import Path

# Add root to path for imports
sys.path.append(os.getcwd())

from tools.document_loader import load_documents_from_folder
from tools.chunker import chunk_loaded_pages
from tools.embedder import ChromaEmbedder

def main():
    upload_dir = "data/uploads"
    print(f"🚀 Starting Bulk Indexing from: {upload_dir}")

    # 1. Load all supported files
    try:
        pages = load_documents_from_folder(upload_dir)
        if not pages:
            print("❌ No documents found to index.")
            return
        print(f"✅ Loaded {len(pages)} pages/slides.")
    except Exception as e:
        print(f"❌ Error loading documents: {e}")
        return

    # 2. Chunk them
    print("✂️ Chunking documents...")
    chunks = chunk_loaded_pages(pages)
    print(f"✅ Created {len(chunks)} semantic chunks.")

    # 3. Index to Chroma
    print("📦 Indexing to ChromaDB (Vertex AI)...")
    try:
        db = ChromaEmbedder()
        db.add_chunks(chunks)
        print("🎉 ALL DOCUMENTS INDEXED SUCCESSFULLY!")
    except Exception as e:
        print(f"❌ Indexing failed: {e}")

if __name__ == "__main__":
    main()
