"""Dependency injection container for service composition."""

from typing import Optional
from app.ports import LLm, TranscriptRepository
from app.application.analyze_service import TranscriptAnalyzerService
from app.infrastructure.repositories import InMemoryTranscriptRepository
from app.logging import get_logger

# Create logger for this module
logger = get_logger(__name__)


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
    logger.info("Creating TranscriptAnalyzerService")
    
    if repository is None:
        logger.info("No repository provided, creating InMemoryTranscriptRepository")
        repository = InMemoryTranscriptRepository()
    else:
        logger.info(f"Using provided repository of type: {type(repository).__name__}")
    
    logger.debug(f"Using LLM adapter of type: {type(llm).__name__}")
    
    service = TranscriptAnalyzerService(
        llm=llm,
        repository=repository
    )
    
    logger.info("TranscriptAnalyzerService created successfully")
    return service 