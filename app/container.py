"""Dependency injection container for service composition."""

from typing import Optional
from app.ports import LLm, TranscriptRepository
from app.application.analyze_service import TranscriptAnalyzerService
from app.infrastructure.repositories import InMemoryTranscriptRepository


def get_service(
    llm: LLm, 
    repository: Optional[TranscriptRepository] = None
) -> TranscriptAnalyzerService:
    """Get a configured TranscriptAnalyzerService instance.
    
    This factory function centralizes service creation to enable easier
    dependency injection for testing.
    
    Args:
        llm: LLM adapter implementation
        repository: Optional repository implementation. If None, an 
            InMemoryTranscriptRepository will be created
            
    Returns:
        Configured TranscriptAnalyzerService
    """
    if repository is None:
        repository = InMemoryTranscriptRepository()
        
    return TranscriptAnalyzerService(
        llm=llm,
        repository=repository
    ) 