import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from tools.document_loader import load_document, load_documents_from_folder
from tools.chunker import chunk_loaded_pages
from tools.embedder import ChromaEmbedder


def index_path(input_path: str):
    load_dotenv()

    path = Path(input_path)

    print(f"Checking path: {path}")

    if not path.exists():
        raise FileNotFoundError(f"Path not found: {input_path}")

    if path.is_dir():
        print(f"Loading documents from folder: {path}")
        loaded_pages = load_documents_from_folder(str(path))
    else:
        print(f"Loading document: {path}")
        loaded_pages = load_document(str(path))

    print(f"Loaded {len(loaded_pages)} pages/slides/text blocks.")

    chunks = chunk_loaded_pages(
        loaded_pages=loaded_pages,
        max_words=180,
        overlap_words=40,
    )

    print(f"Created {len(chunks)} chunks.")

    embedder = ChromaEmbedder()
    embedder.add_chunks(chunks)

    print("Indexing complete.")


if __name__ == "__main__":
    print("Starting document indexing script...")

    if len(sys.argv) < 2:
        print("Usage:")
        print("py scripts/index_documents.py data/uploads")
        print("py scripts/index_documents.py data/uploads/lecture1.pdf")
        sys.exit(1)

    index_path(sys.argv[1])