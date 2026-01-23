import uuid
from pydantic import BaseModel, Field


class TranscriptAnalysis(BaseModel):
    """Domain model representing the analysis of a transcript"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    summary: str
    action_items: list[str] 