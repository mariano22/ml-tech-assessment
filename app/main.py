from fastapi import FastAPI, status, Depends
from app import configurations
from app.adapters.inbound.rest import build_router
from app.adapters.openai import OpenAIAdapter
from app.container import get_service
from app.ports import LLm, TranscriptAnalyzer


def create_app(llm_adapter: LLm = None) -> FastAPI:
    """Create and configure the FastAPI application
    
    Args:
        llm_adapter: Optional LLM adapter for testing purposes
    
    Returns:
        Configured FastAPI application
    """
    # Load configuration
    env = configurations.EnvConfigs()
    
    # Create dependencies
    if llm_adapter is None:
        llm_adapter = OpenAIAdapter(api_key=env.OPENAI_API_KEY, model=env.OPENAI_MODEL)
    
    analyzer_service = get_service(llm=llm_adapter)
    
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