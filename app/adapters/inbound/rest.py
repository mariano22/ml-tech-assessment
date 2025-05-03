import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.domain.models import TranscriptAnalysis
from app.ports import TranscriptAnalyzer


class TranscriptRequest(BaseModel):
    """API request model for transcript analysis"""
    transcript: str


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
            analysis = analyzer_service.analyze(transcript)
            return AnalysisResponse.from_domain(analysis)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.post("/analyze", response_model=AnalysisResponse)
    async def analyze_transcript_post(
        request: TranscriptRequest
    ) -> AnalysisResponse:
        """Analyze a transcript to generate a summary and action items (POST method)"""
        try:
            analysis = analyzer_service.analyze(request.transcript)
            return AnalysisResponse.from_domain(analysis)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.get("/{analysis_id}", response_model=AnalysisResponse)
    async def get_analysis(analysis_id: uuid.UUID) -> AnalysisResponse:
        """Get a previously generated transcript analysis by ID"""
        try:
            analysis = analyzer_service.get_analysis(analysis_id)
            return AnalysisResponse.from_domain(analysis)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    
    return router 