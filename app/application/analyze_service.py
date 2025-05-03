import uuid
import pydantic
from app.domain.models import TranscriptAnalysis
from app.ports import LLm, TranscriptAnalyzer, TranscriptRepository
from app.prompts import SYSTEM_PROMPT, RAW_USER_PROMPT


class AnalysisDTO(pydantic.BaseModel):
    """Data transfer object for LLM response"""
    summary: str
    action_items: list[str]


class TranscriptAnalyzerService(TranscriptAnalyzer):
    """Service implementation for analyzing transcripts using an LLM"""
    
    def __init__(self, llm: LLm, repository: TranscriptRepository) -> None:
        self._llm = llm
        self._repository = repository
    
    def analyze(self, transcript: str) -> TranscriptAnalysis:
        """Analyze a transcript using the LLM and store the result"""
        if not transcript or transcript.isspace():
            raise ValueError("Transcript cannot be empty")
        
        user_prompt = RAW_USER_PROMPT.format(transcript=transcript)
        llm_response = self._llm.run_completion(
            SYSTEM_PROMPT, 
            user_prompt, 
            AnalysisDTO
        )
        
        analysis = TranscriptAnalysis(
            summary=llm_response.summary,
            action_items=llm_response.action_items
        )
        
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
        return self._repository.get(analysis_id) 