import uuid
import asyncio
from app.domain.models import TranscriptAnalysis
from app.domain.exceptions import EmptyTranscriptError, InvalidBatchError, TranscriptNotFoundError
from app.dto.analysis import AnalysisDTO
from app.ports import LLm, TranscriptAnalyzer, TranscriptRepository
from app.prompts import SYSTEM_PROMPT, RAW_USER_PROMPT
from app.logging import get_logger

# Create logger for this module
logger = get_logger(__name__)


class TranscriptAnalyzerService(TranscriptAnalyzer):
    """Service implementation for analyzing transcripts using an LLM"""
    
    def __init__(self, llm: LLm, repository: TranscriptRepository) -> None:
        self._llm = llm
        self._repository = repository
        logger.info("TranscriptAnalyzerService initialized")
    
    def analyze(self, transcript: str) -> TranscriptAnalysis:
        """Analyze a transcript using the LLM and store the result"""
        logger.info("Analyzing transcript (sync method)")
        
        if not transcript or transcript.isspace():
            logger.warning("Empty transcript provided")
            raise EmptyTranscriptError("Transcript cannot be empty")
        
        logger.debug(f"Transcript length: {len(transcript)} characters")
        user_prompt = RAW_USER_PROMPT.format(transcript=transcript)
        
        logger.debug("Calling LLM for completion")
        llm_response = self._llm.run_completion(
            SYSTEM_PROMPT, 
            user_prompt, 
            AnalysisDTO
        )
        
        # Convert DTO to domain model
        logger.debug("Converting DTO to domain model")
        analysis = llm_response.to_domain_model()
        
        logger.debug(f"Saving analysis with ID: {analysis.id}")
        self._repository.save(analysis)
        
        logger.info(f"Analysis complete with ID: {analysis.id}")
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
        logger.info(f"Retrieving analysis with ID: {analysis_id}")
        try:
            analysis = self._repository.get(analysis_id)
            logger.debug(f"Analysis found with ID: {analysis_id}")
            return analysis
        except ValueError as exc:
            # Convert to domain-specific error
            logger.warning(f"Analysis not found with ID: {analysis_id}")
            raise TranscriptNotFoundError(str(exc)) from exc
        
    async def analyze_async(self, transcript: str) -> TranscriptAnalysis:
        """Asynchronously analyze a transcript using the LLM and store the result"""
        logger.info("Analyzing transcript (async method)")
        
        if not transcript or transcript.isspace():
            logger.warning("Empty transcript provided")
            raise EmptyTranscriptError("Transcript cannot be empty")
        
        logger.debug(f"Transcript length: {len(transcript)} characters")
        user_prompt = RAW_USER_PROMPT.format(transcript=transcript)
        
        logger.debug("Calling LLM for async completion")
        llm_response = await self._llm.run_completion_async(
            SYSTEM_PROMPT, 
            user_prompt, 
            AnalysisDTO
        )
        
        # Convert DTO to domain model
        logger.debug("Converting DTO to domain model")
        analysis = llm_response.to_domain_model()
        
        logger.debug(f"Saving analysis with ID: {analysis.id}")
        self._repository.save(analysis)
        
        logger.info(f"Async analysis complete with ID: {analysis.id}")
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
        logger.info(f"Starting batch analysis of {len(transcripts) if transcripts else 0} transcripts")
        
        if not transcripts:
            logger.warning("Empty batch provided")
            raise InvalidBatchError("No transcripts provided")
            
        # Additional validation to check for empty transcripts
        if any(not t or t.isspace() for t in transcripts):
            logger.warning("Batch contains empty transcripts")
            raise InvalidBatchError("All transcripts must be non-empty")
        
        logger.debug(f"Creating {len(transcripts)} coroutines for parallel execution")    
        # Create a list of coroutines for parallel execution
        analysis_coroutines = [self.analyze_async(transcript) for transcript in transcripts]
        
        # Run all analysis tasks concurrently
        logger.info(f"Starting concurrent analysis of {len(transcripts)} transcripts")
        results = await asyncio.gather(*analysis_coroutines)
        logger.info(f"Batch analysis complete, processed {len(results)} transcripts")
        
        return results 