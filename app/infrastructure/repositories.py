import uuid
from app.domain.models import TranscriptAnalysis
from app.ports import TranscriptRepository
from app.logging import get_logger

# Create logger for this module
logger = get_logger(__name__)


class InMemoryTranscriptRepository(TranscriptRepository):
    """In-memory implementation of the transcript repository"""
    
    def __init__(self) -> None:
        self._storage = {}  # uuid -> TranscriptAnalysis
        logger.info("InMemoryTranscriptRepository initialized")
    
    def save(self, analysis: TranscriptAnalysis) -> None:
        """Save a transcript analysis to the in-memory storage"""
        logger.debug(f"Saving analysis with ID: {analysis.id}")
        
        # Check if we're updating an existing analysis
        is_update = analysis.id in self._storage
        
        self._storage[analysis.id] = analysis
        
        if is_update:
            logger.info(f"Updated existing analysis with ID: {analysis.id}")
        else:
            logger.info(f"Saved new analysis with ID: {analysis.id}")
            logger.debug(f"Current repository size: {len(self._storage)} items")
    
    def get(self, id: uuid.UUID) -> TranscriptAnalysis:
        """Retrieve a transcript analysis by ID
        
        Raises:
            ValueError: If no analysis with the given ID exists
        """
        logger.debug(f"Attempting to retrieve analysis with ID: {id}")
        
        if id not in self._storage:
            logger.warning(f"Analysis not found with ID: {id}")
            raise ValueError(f"No transcript analysis found with id: {id}")
        
        logger.debug(f"Successfully retrieved analysis with ID: {id}")
        return self._storage[id] 