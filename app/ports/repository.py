from abc import ABC, abstractmethod
import uuid
from typing import List
from app.domain.models import TranscriptAnalysis


class TranscriptRepository(ABC):
    """Interface for transcript analysis repository operations"""
    
    @abstractmethod
    def save(self, analysis: TranscriptAnalysis) -> None:
        """Save a transcript analysis to the repository"""
        pass
    
    @abstractmethod
    def get(self, id: uuid.UUID) -> TranscriptAnalysis:
        """Retrieve a transcript analysis by ID
        
        Raises:
            ValueError: If no analysis with the given ID exists
        """
        pass
    
    @abstractmethod
    def list(self) -> List[TranscriptAnalysis]:
        """Retrieve all transcript analyses
        
        Returns:
            List of all transcript analyses stored in the repository
        """
        pass 