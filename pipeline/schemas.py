from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class KeyIdea(BaseModel):
    """Output of Member 1's Decomposer"""
    name: str
    description: str

class Chunk(BaseModel):
    """Output of Member 2's Document Loader"""
    text: str
    metadata: Dict[str, Any]
    pedagogical_score: Optional[float] = None  # Filled by Member 1's TARJ

class CoverageReport(BaseModel):
    """Output of Member 2's ECV Verifier"""
    key_ideas_status: Dict[str, str]  # e.g., {"Backprop": "covered", "Chain Rule": "missing"}
    supplement: Optional[str] = None

class DebtEntry(BaseModel):
    """Output of Member 2's Debt Detector, used by Member 1's Explainer"""
    prerequisite_concept: str
    severity: int  # 1-5
    evidence: str
