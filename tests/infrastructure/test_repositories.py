"""Unit tests for repository implementations."""

import uuid
import pytest
from app.domain.models import TranscriptAnalysis
from app.infrastructure.repositories import InMemoryTranscriptRepository


class TestInMemoryTranscriptRepository:
    """Test suite for the in-memory transcript repository."""
    
    def setup_method(self):
        """Set up a fresh repository for each test."""
        self.repository = InMemoryTranscriptRepository()
    
    def test_save_and_get(self):
        """Test saving and retrieving a transcript analysis."""
        # Arrange
        analysis = TranscriptAnalysis(
            summary="Test summary",
            action_items=["Action 1", "Action 2"]
        )
        
        # Act
        self.repository.save(analysis)
        retrieved = self.repository.get(analysis.id)
        
        # Assert
        assert retrieved == analysis
        assert retrieved.id == analysis.id
        assert retrieved.summary == "Test summary"
        assert retrieved.action_items == ["Action 1", "Action 2"]
    
    def test_save_updates_existing(self):
        """Test that saving with same ID updates rather than creates."""
        # Arrange
        analysis_id = uuid.uuid4()
        analysis1 = TranscriptAnalysis(
            id=analysis_id,
            summary="Original summary",
            action_items=["Original action"]
        )
        analysis2 = TranscriptAnalysis(
            id=analysis_id,
            summary="Updated summary",
            action_items=["Updated action"]
        )
        
        # Act
        self.repository.save(analysis1)
        self.repository.save(analysis2)  # Same ID
        retrieved = self.repository.get(analysis_id)
        
        # Assert
        assert retrieved.summary == "Updated summary"
        assert retrieved.action_items == ["Updated action"]
        
    def test_get_nonexistent(self):
        """Test that getting a non-existent ID raises ValueError."""
        # Arrange
        nonexistent_id = uuid.uuid4()
        
        # Act & Assert
        with pytest.raises(ValueError, match="No transcript analysis found with id"):
            self.repository.get(nonexistent_id)
    
    def test_multiple_entries(self):
        """Test repository can handle multiple analyses."""
        # Arrange
        analysis1 = TranscriptAnalysis(
            summary="Summary 1",
            action_items=["Action 1"]
        )
        analysis2 = TranscriptAnalysis(
            summary="Summary 2", 
            action_items=["Action 2"]
        )
        
        # Act
        self.repository.save(analysis1)
        self.repository.save(analysis2)
        
        # Assert - both retrievable by their IDs
        retrieved1 = self.repository.get(analysis1.id)
        retrieved2 = self.repository.get(analysis2.id)
        
        assert retrieved1.summary == "Summary 1"
        assert retrieved2.summary == "Summary 2" 