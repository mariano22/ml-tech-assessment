import uuid
import pytest
from unittest.mock import MagicMock, AsyncMock
import asyncio

from app.application.analyze_service import TranscriptAnalyzerService, AnalysisDTO
from app.domain.models import TranscriptAnalysis
from app.ports import LLm, TranscriptRepository


class TestTranscriptAnalyzerService:
    def setup_method(self):
        self.mock_llm = MagicMock()
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
        
    @pytest.mark.asyncio
    async def test_analyze_async(self):
        # Arrange
        transcript = "This is a test transcript"
        mock_llm_response = AnalysisDTO(
            summary="Test summary",
            action_items=["Action 1", "Action 2"]
        )
        
        # Convert to AsyncMock for the async method
        self.mock_llm.run_completion_async = AsyncMock(return_value=mock_llm_response)
        
        # Act
        result = await self.service.analyze_async(transcript)
        
        # Assert
        assert isinstance(result, TranscriptAnalysis)
        assert result.summary == "Test summary"
        assert result.action_items == ["Action 1", "Action 2"]
        self.mock_repository.save.assert_called_once()
        self.mock_llm.run_completion_async.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_analyze_async_with_empty_transcript(self):
        # Arrange
        self.mock_llm.run_completion_async = AsyncMock()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Transcript cannot be empty"):
            await self.service.analyze_async("")
        
        with pytest.raises(ValueError, match="Transcript cannot be empty"):
            await self.service.analyze_async("   ")
        
        self.mock_llm.run_completion_async.assert_not_called()
        self.mock_repository.save.assert_not_called()
        
    @pytest.mark.asyncio
    async def test_analyze_many(self):
        # Arrange
        transcripts = ["Transcript 1", "Transcript 2", "Transcript 3"]
        
        # Setup mock for async analyze to return different analyses
        async def mock_analyze_async(transcript):
            analysis = TranscriptAnalysis(
                summary=f"Summary for {transcript}",
                action_items=[f"Action for {transcript}"]
            )
            return analysis
            
        # Replace the method with our mock
        self.service.analyze_async = AsyncMock(side_effect=mock_analyze_async)  # type: ignore
        
        # Act
        results = await self.service.analyze_many(transcripts)
        
        # Assert
        assert len(results) == 3
        assert all(isinstance(result, TranscriptAnalysis) for result in results)
        assert results[0].summary == "Summary for Transcript 1"
        assert results[1].summary == "Summary for Transcript 2"
        assert results[2].summary == "Summary for Transcript 3"
        assert self.service.analyze_async.call_count == 3
        
    @pytest.mark.asyncio
    async def test_analyze_many_with_empty_list(self):
        # Act & Assert
        with pytest.raises(ValueError, match="No transcripts provided"):
            await self.service.analyze_many([])
            
        # No methods should be called
        self.mock_llm.run_completion_async.assert_not_called()
        self.mock_repository.save.assert_not_called() 