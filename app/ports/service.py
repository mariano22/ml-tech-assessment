from abc import ABC, abstractmethod
import uuid
from typing import List
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
    
    @abstractmethod
    def list_all(self) -> List[TranscriptAnalysis]:
        """List all transcript analyses
        
        Returns:
            List of all transcript analyses
        """
        pass
        
    @abstractmethod
    async def analyze_async(self, transcript: str) -> TranscriptAnalysis:
        """Asynchronously analyze a transcript to generate a summary and action items
        
        Args:
            transcript: The text transcript to analyze
            
        Returns:
            TranscriptAnalysis: Analysis results with summary and action items
            
        Raises:
            ValueError: If the transcript is empty
        """
        pass
        
    @abstractmethod
    async def analyze_many(self, transcripts: list[str]) -> list[TranscriptAnalysis]:
        """Concurrently analyze multiple transcripts
        
        Args:
            transcripts: List of transcript texts to analyze
            
        Returns:
            List of analysis results with summaries and action items
            
        Raises:
            ValueError: If the transcripts list is empty or contains empty transcripts
        """
        pass 