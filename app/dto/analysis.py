"""DTOs for transcript analysis and LLM responses."""

import pydantic
from typing import List, Optional
from uuid import UUID, uuid4

from app.domain.models import TranscriptAnalysis


class AnalysisDTO(pydantic.BaseModel):
    """Data transfer object for LLM structured responses.
    
    This represents the raw data returned from the LLM service
    before conversion to a domain model.
    """
    summary: str
    action_items: List[str]
    
    def to_domain_model(self, id: Optional[UUID] = None) -> TranscriptAnalysis:
        """Convert DTO to domain model
        
        Args:
            id: Optional UUID to use for the domain model. If not provided,
                a new UUID will be generated.
                
        Returns:
            TranscriptAnalysis domain model
        """
        return TranscriptAnalysis(
            id=id or uuid4(),
            summary=self.summary,
            action_items=self.action_items
        ) 