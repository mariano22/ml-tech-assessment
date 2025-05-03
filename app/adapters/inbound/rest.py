import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from app.domain.models import TranscriptAnalysis
from app.ports import TranscriptAnalyzer
from app.domain.exceptions import EmptyTranscriptError, InvalidBatchError, TranscriptNotFoundError
from app.schemas.http_error import HTTPError
from app.logging import get_logger

# Create logger for this module
logger = get_logger(__name__)


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
    logger.info("Building API router")
    router = APIRouter(prefix="/transcripts", tags=["transcripts"])
    
    @router.post("", response_model=AnalysisResponse, responses={400: {"model": HTTPError}})
    async def create_transcript_analysis(
        request: Request,
        body: TranscriptRequest
    ) -> AnalysisResponse:
        """Create a new transcript analysis by analyzing the provided transcript"""
        client_host = request.client.host if request.client else "unknown"
        logger.info(f"POST /transcripts request received from {client_host}")
        logger.debug(f"Transcript length: {len(body.transcript)} characters")
        
        try:
            analysis = await analyzer_service.analyze_async(body.transcript)
            logger.info(f"Analysis created successfully, ID: {analysis.id}")
            return AnalysisResponse.from_domain(analysis)
        except EmptyTranscriptError as e:
            logger.warning(f"Bad request from {client_host}: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.post("/batch", response_model=BatchAnalysisResponse, responses={400: {"model": HTTPError}})
    async def create_batch_analyses(
        request: Request,
        body: BatchTranscriptRequest
    ) -> BatchAnalysisResponse:
        """Create multiple transcript analyses concurrently"""
        client_host = request.client.host if request.client else "unknown"
        logger.info(f"POST /transcripts/batch request received from {client_host} with {len(body.transcripts)} transcripts")
        
        try:
            analyses = await analyzer_service.analyze_many(body.transcripts)
            
            response_items = [AnalysisResponse.from_domain(analysis) for analysis in analyses]
            logger.info(f"Batch analysis complete, created {len(response_items)} analyses")
            
            return BatchAnalysisResponse(results=response_items)
        except InvalidBatchError as e:
            logger.warning(f"Bad batch request from {client_host}: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.get("", response_model=List[AnalysisResponse])
    async def list_transcript_analyses(
        request: Request
    ) -> List[AnalysisResponse]:
        """List all transcript analyses"""
        client_host = request.client.host if request.client else "unknown"
        logger.info(f"GET /transcripts request received from {client_host}")
        
        analyses = analyzer_service.list_all()
        response_items = [AnalysisResponse.from_domain(analysis) for analysis in analyses]
        
        logger.info(f"Returning list of {len(response_items)} analyses")
        return response_items
    
    @router.get("/{analysis_id}", response_model=AnalysisResponse, responses={404: {"model": HTTPError}})
    async def get_analysis(
        request: Request,
        analysis_id: uuid.UUID
    ) -> AnalysisResponse:
        """Get a transcript analysis by ID"""
        client_host = request.client.host if request.client else "unknown"
        logger.info(f"GET /transcripts/{analysis_id} request received from {client_host}")
        
        try:
            analysis = analyzer_service.get_analysis(analysis_id)
            logger.info(f"Retrieved analysis with ID: {analysis_id}")
            return AnalysisResponse.from_domain(analysis)
        except TranscriptNotFoundError as e:
            logger.warning(f"Analysis not found for ID: {analysis_id}")
            raise HTTPException(status_code=404, detail=str(e))
    
    @router.get("/health")
    async def health_check(request: Request) -> dict:
        """Check the health of the application"""
        client_host = request.client.host if request.client else "unknown"
        logger.debug(f"Health check request from {client_host}")
        return {"status": "healthy"}
    
    logger.info("API router built successfully")
    return router 