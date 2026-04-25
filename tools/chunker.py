from typing import Any, Dict, List

from schemas import Chunk


def chunk_text(
    text: str,
    source_file: str,
    page_number=None,
    max_words: int = 180,
    overlap_words: int = 40,
) -> List[Chunk]:
    """
    Splits one text block into overlapping chunks.
    """
    words = text.split()

    if not words:
        return []

    chunks = []
    start = 0
    chunk_index = 0

    while start < len(words):
        end = start + max_words
        chunk_words = words[start:end]
        chunk_content = " ".join(chunk_words)

        chunk_id = f"{source_file}_page_{page_number}_chunk_{chunk_index}"

        chunk = Chunk(
            chunk_id=chunk_id,
            text=chunk_content,
            source_file=source_file,
            page_number=page_number,
            chunk_index=chunk_index,
            metadata={
                "source_file": source_file,
                "filename": source_file,
                "page": page_number,
                "page_number": page_number,
                "chunk_index": chunk_index,
            },
        )

        chunks.append(chunk)

        if end >= len(words):
            break

        start += max_words - overlap_words
        chunk_index += 1

    return chunks


def chunk_loaded_pages(
    loaded_pages: List[Dict[str, Any]],
    max_words: int = 180,
    overlap_words: int = 40,
) -> List[Chunk]:
    """
    Converts loaded document pages/slides into chunks.
    Input comes from document_loader.py.
    """
    all_chunks = []

    for page in loaded_pages:
        text = page.get("text", "")
        source_file = page.get("source_file", "unknown_source")
        page_number = page.get("page_number")

        chunks = chunk_text(
            text=text,
            source_file=source_file,
            page_number=page_number,
            max_words=max_words,
            overlap_words=overlap_words,
        )

        for chunk in chunks:
            chunk.metadata["file_type"] = page.get("file_type")

        all_chunks.extend(chunks)

    return all_chunks