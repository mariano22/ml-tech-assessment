from fastapi import FastAPI, status
from app import configurations
from app.adapters.inbound.rest import build_router
from app.adapters.openai import OpenAIAdapter
from app.application.analyze_service import TranscriptAnalyzerService
from app.infrastructure.repositories import InMemoryTranscriptRepository


def create_app() -> FastAPI:
    """Create and configure the FastAPI application
    
    Returns:
        Configured FastAPI application
    """
    # Load configuration
    env = configurations.EnvConfigs()
    
    # Set up dependencies
    llm_adapter = OpenAIAdapter(
        api_key=env.OPENAI_API_KEY,
        model=env.OPENAI_MODEL
    )
    repository = InMemoryTranscriptRepository()
    analyzer_service = TranscriptAnalyzerService(
        llm=llm_adapter,
        repository=repository
    )
    
    # Create and configure FastAPI app
    app = FastAPI(
        title="Transcript Analysis API",
        description="API for analyzing text transcripts and providing summaries and action items",
        version="1.0.0",
        docs_url="/swagger",
    )
    
    # Register routes
    router = build_router(analyzer_service)
    app.include_router(router)
    
    # Add health check endpoint
    @app.get("/health", status_code=status.HTTP_200_OK, tags=["health"])
    def health_check():
        """Health check endpoint for monitoring and container health checks"""
        return {"status": "healthy"}
    
    return app


app = create_app() 