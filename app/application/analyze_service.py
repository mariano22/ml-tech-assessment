import uuid
import asyncio
from app.domain.models import TranscriptAnalysis
from app.domain.exceptions import EmptyTranscriptError, InvalidBatchError, TranscriptNotFoundError
from app.dto.analysis import AnalysisDTO
from app.ports import LLm, TranscriptAnalyzer, TranscriptRepository
from app.prompts import SYSTEM_PROMPT, RAW_USER_PROMPT


class TranscriptAnalyzerService(TranscriptAnalyzer):
    """Service implementation for analyzing transcripts using an LLM"""
    
    def __init__(self, llm: LLm, repository: TranscriptRepository) -> None:
        self._llm = llm
        self._repository = repository
    
    def analyze(self, transcript: str) -> TranscriptAnalysis:
        """Analyze a transcript using the LLM and store the result"""
        if not transcript or transcript.isspace():
            raise EmptyTranscriptError("Transcript cannot be empty")
        
        user_prompt = RAW_USER_PROMPT.format(transcript=transcript)
        llm_response = self._llm.run_completion(
            SYSTEM_PROMPT, 
            user_prompt, 
            AnalysisDTO
        )
        
        # Convert DTO to domain model
        analysis = llm_response.to_domain_model()
        
        self._repository.save(analysis)
        return analysis
    
    def get_analysis(self, analysis_id: uuid.UUID) -> TranscriptAnalysis:
        """Retrieve a previously generated transcript analysis
        
        Args:
            analysis_id: UUID of the analysis to retrieve
            
        Returns:
            The transcript analysis
            
        Raises:
            ValueError: If no analysis with the given ID exists
        """
        try:
            return self._repository.get(analysis_id)
        except ValueError as exc:
            # Convert to domain-specific error
            raise TranscriptNotFoundError(str(exc)) from exc
        
    async def analyze_async(self, transcript: str) -> TranscriptAnalysis:
        """Asynchronously analyze a transcript using the LLM and store the result"""
        if not transcript or transcript.isspace():
            raise EmptyTranscriptError("Transcript cannot be empty")
        
        user_prompt = RAW_USER_PROMPT.format(transcript=transcript)
        llm_response = await self._llm.run_completion_async(
            SYSTEM_PROMPT, 
            user_prompt, 
            AnalysisDTO
        )
        
        # Convert DTO to domain model
        analysis = llm_response.to_domain_model()
        
        self._repository.save(analysis)
        return analysis
        
    async def analyze_many(self, transcripts: list[str]) -> list[TranscriptAnalysis]:
        """Concurrently analyze multiple transcripts
        
        Args:
            transcripts: List of transcript texts to analyze
            
        Returns:
            List of analysis results with summaries and action items
            
        Raises:
            ValueError: If the transcripts list is empty or contains empty transcripts
        """
        if not transcripts:
            raise InvalidBatchError("No transcripts provided")
            
        # Additional validation to check for empty transcripts
        if any(not t or t.isspace() for t in transcripts):
            raise InvalidBatchError("All transcripts must be non-empty")
            
        # Create a list of coroutines for parallel execution
        analysis_coroutines = [self.analyze_async(transcript) for transcript in transcripts]
        
        # Run all analysis tasks concurrently
        return await asyncio.gather(*analysis_coroutines) 