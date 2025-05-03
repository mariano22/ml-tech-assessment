import uuid
import pytest
from unittest.mock import MagicMock

from app.application.analyze_service import TranscriptAnalyzerService, AnalysisDTO
from app.domain.models import TranscriptAnalysis
from app.ports import LLm, TranscriptRepository


class TestTranscriptAnalyzerService:
    def setup_method(self):
        self.mock_llm = MagicMock(spec=LLm)
        self.mock_repository = MagicMock(spec=TranscriptRepository)
        self.service = TranscriptAnalyzerService(
            llm=self.mock_llm,
            repository=self.mock_repository
        )
        
    def test_analyze_with_valid_transcript(self):
        # Arrange
        transcript = "This is a test transcript"
        mock_llm_response = AnalysisDTO(
            summary="Test summary",
            action_items=["Action 1", "Action 2"]
        )
        self.mock_llm.run_completion.return_value = mock_llm_response
        
        # Act
        result = self.service.analyze(transcript)
        
        # Assert
        assert isinstance(result, TranscriptAnalysis)
        assert result.summary == "Test summary"
        assert result.action_items == ["Action 1", "Action 2"]
        self.mock_repository.save.assert_called_once()
        
    def test_analyze_with_empty_transcript(self):
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Transcript cannot be empty"):
            self.service.analyze("")
        
        with pytest.raises(ValueError, match="Transcript cannot be empty"):
            self.service.analyze("   ")
        
        self.mock_llm.run_completion.assert_not_called()
        self.mock_repository.save.assert_not_called()
    
    def test_get_analysis(self):
        # Arrange
        analysis_id = uuid.uuid4()
        expected_analysis = TranscriptAnalysis(
            id=analysis_id,
            summary="Test summary",
            action_items=["Action 1", "Action 2"]
        )
        self.mock_repository.get.return_value = expected_analysis
        
        # Act
        result = self.service.get_analysis(analysis_id)
        
        # Assert
        assert result == expected_analysis
        self.mock_repository.get.assert_called_once_with(analysis_id)
    
    def test_get_analysis_not_found(self):
        # Arrange
        analysis_id = uuid.uuid4()
        self.mock_repository.get.side_effect = ValueError("Not found")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Not found"):
            self.service.get_analysis(analysis_id)
        
        self.mock_repository.get.assert_called_once_with(analysis_id) 