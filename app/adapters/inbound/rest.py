import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.domain.models import TranscriptAnalysis
from app.ports import TranscriptAnalyzer
from app.domain.exceptions import EmptyTranscriptError, InvalidBatchError, TranscriptNotFoundError


class TranscriptRequest(BaseModel):
    """API request model for transcript analysis"""
    transcript: str


class BatchTranscriptRequest(BaseModel):
    """API request model for batch transcript analysis"""
    transcripts: List[str]


class AnalysisResponse(BaseModel):
    """API response model for transcript analysis"""
    id: uuid.UUID
    summary: str
    action_items: list[str]
    
    @classmethod
    def from_domain(cls, analysis: TranscriptAnalysis) -> "AnalysisResponse":
        """Convert domain model to API response model"""
        return cls(
            id=analysis.id,
            summary=analysis.summary,
            action_items=analysis.action_items
        )


class BatchAnalysisResponse(BaseModel):
    """API response model for batch transcript analysis"""
    results: List[AnalysisResponse]


def build_router(analyzer_service: TranscriptAnalyzer) -> APIRouter:
    """Build and configure the API router
    
    Args:
        analyzer_service: Service for analyzing transcripts
        
    Returns:
        Configured FastAPI router
    """
    router = APIRouter(prefix="/transcripts", tags=["transcripts"])
    
    @router.get("/analyze", response_model=AnalysisResponse)
    async def analyze_transcript_get(
        transcript: Annotated[str, Query(description="The transcript text to analyze")]
    ) -> AnalysisResponse:
        """Analyze a transcript to generate a summary and action items (GET method)"""
        try:
            analysis = await analyzer_service.analyze_async(transcript)
            return AnalysisResponse.from_domain(analysis)
        except EmptyTranscriptError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.post("/analyze", response_model=AnalysisResponse)
    async def analyze_transcript_post(
        request: TranscriptRequest
    ) -> AnalysisResponse:
        """Analyze a transcript to generate a summary and action items (POST method)"""
        try:
            analysis = await analyzer_service.analyze_async(request.transcript)
            return AnalysisResponse.from_domain(analysis)
        except EmptyTranscriptError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.post("/analyze/batch", response_model=BatchAnalysisResponse)
    async def analyze_transcripts_batch(
        request: BatchTranscriptRequest
    ) -> BatchAnalysisResponse:
        """Concurrently analyze multiple transcripts to generate summaries and action items"""
        try:
            analyses = await analyzer_service.analyze_many(request.transcripts)
            
            response_items = [AnalysisResponse.from_domain(analysis) for analysis in analyses]
            
            return BatchAnalysisResponse(results=response_items)
        except InvalidBatchError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.get("/{analysis_id}", response_model=AnalysisResponse)
    async def get_analysis(analysis_id: uuid.UUID) -> AnalysisResponse:
        """Get a previously generated transcript analysis by ID"""
        try:
            analysis = analyzer_service.get_analysis(analysis_id)
            return AnalysisResponse.from_domain(analysis)
        except TranscriptNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
    
    return router 