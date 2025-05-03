import uuid
from app.domain.models import TranscriptAnalysis
from app.ports import TranscriptRepository


class InMemoryTranscriptRepository(TranscriptRepository):
    """In-memory implementation of the transcript repository"""
    
    def __init__(self) -> None:
        self._storage = {}  # uuid -> TranscriptAnalysis
    
    def save(self, analysis: TranscriptAnalysis) -> None:
        """Save a transcript analysis to the in-memory storage"""
        self._storage[analysis.id] = analysis
    
    def get(self, id: uuid.UUID) -> TranscriptAnalysis:
        """Retrieve a transcript analysis by ID
        
        Raises:
            ValueError: If no analysis with the given ID exists
        """
        if id not in self._storage:
            raise ValueError(f"No transcript analysis found with id: {id}")
        return self._storage[id] 