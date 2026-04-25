from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Chunk:
    chunk_id: str
    text: str
    source_file: str
    page_number: Optional[int] = None
    chunk_index: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KeyIdea:
    idea_id: str
    text: str
    importance: int = 3


@dataclass
class CoverageReport:
    is_complete: bool
    score: float
    covered_ideas: List[str]
    missing_ideas: List[str]
    feedback: str


@dataclass
class DebtEntry:
    topic: str
    missing_concept: str
    reason: str
    severity: int = 3