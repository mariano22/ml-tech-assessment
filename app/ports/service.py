from abc import ABC, abstractmethod
import uuid
from app.domain.models import TranscriptAnalysis


class TranscriptAnalyzer(ABC):
    """Interface for transcript analysis service"""
    
    @abstractmethod
    def analyze(self, transcript: str) -> TranscriptAnalysis:
        """Analyze a transcript to generate a summary and action items
        
        Args:
            transcript: The text transcript to analyze
            
        Returns:
            TranscriptAnalysis: Analysis results with summary and action items
            
        Raises:
            ValueError: If the transcript is empty
        """
        pass
    
    @abstractmethod
    def get_analysis(self, analysis_id: uuid.UUID) -> TranscriptAnalysis:
        """Retrieve a previously generated transcript analysis
        
        Args:
            analysis_id: UUID of the analysis to retrieve
            
        Returns:
            The transcript analysis
            
        Raises:
            ValueError: If no analysis with the given ID exists
        """
        pass 