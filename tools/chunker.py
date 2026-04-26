import uuid
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pipeline.schemas import Chunk

def chunk_loaded_pages(pages: List[Dict[str, Any]], chunk_size: int = 500, chunk_overlap: int = 50) -> List[Chunk]:
    """
    Splits loaded pages into smaller semantic chunks while PRESERVING all metadata (student_id, file_type, etc).
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )

    chunks = []
    
    for page in pages:
        text = page.get("text", "")
        # Split the text of this specific page
        texts = text_splitter.split_text(text)
        
        for i, split_text in enumerate(texts):
            # Create a unique ID for this chunk
            chunk_id = str(uuid.uuid4())
            
            # Create the Chunk object, carrying over EVERYTHING from the page dict
            chunks.append(Chunk(
                chunk_id=chunk_id,
                text=split_text,
                source_file=page.get("source_file"),
                page_number=page.get("page_number"),
                chunk_index=i,
                metadata=page # This now contains student_id, file_type, etc.
            ))

    return chunks
