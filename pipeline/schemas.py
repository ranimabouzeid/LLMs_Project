from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class KeyIdea(BaseModel):
    """Output of Member 1's Decomposer"""
    name: str
    description: str

class Chunk(BaseModel):
    """Output of Member 2's Document Loader"""
    chunk_id: Optional[str] = None
    text: str
    source_file: Optional[str] = None
    page_number: Optional[int] = None
    chunk_index: Optional[int] = None
    metadata: Dict[str, Any]
    pedagogical_score: Optional[float] = None  # Filled by Member 1's TARJ

class CoverageReport(BaseModel):
    """Output of Member 2's ECV Verifier"""
    is_complete: bool
    score: float
    covered_ideas: List[str]
    missing_ideas: List[str]
    feedback: str
    supplement: Optional[str] = None

class DebtEntry(BaseModel):
    """Output of Member 2's Debt Detector, used by Member 1's Explainer"""
    topic: str
    prerequisite_concept: str
    severity: int  # 1-5
    evidence: str
