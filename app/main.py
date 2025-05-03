from fastapi import FastAPI, status, Depends
from contextlib import asynccontextmanager
from app import configurations
from app.adapters.inbound.rest import build_router
from app.adapters.openai import OpenAIAdapter
from app.container import get_service
from app.ports import LLm, TranscriptAnalyzer
from app.logging import configure_logging, get_logger

# Create a logger for this module
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application startup and shutdown events"""
    # Startup event
    logger.info("Application startup complete")
    yield
    # Shutdown event
    logger.info("Application shutting down")


def create_app(llm_adapter: LLm = None) -> FastAPI:
    """Create and configure the FastAPI application
    
    Args:
        llm_adapter: Optional LLM adapter for testing purposes
    
    Returns:
        Configured FastAPI application
    """
    # Load configuration
    env = configurations.EnvConfigs()
    
    # Configure logging
    configure_logging(env.LOG_LEVEL)
    logger.info(f"Starting Transcript Analysis API with log level: {env.LOG_LEVEL}")
    logger.debug(f"Using OpenAI model: {env.OPENAI_MODEL}")
    
    # Create dependencies
    if llm_adapter is None:
        logger.info("Creating OpenAI adapter")
        llm_adapter = OpenAIAdapter(api_key=env.OPENAI_API_KEY, model=env.OPENAI_MODEL)
    else:
        logger.info("Using provided LLM adapter")
    
    analyzer_service = get_service(llm=llm_adapter)
    
    # Create and configure FastAPI app
    logger.info("Configuring FastAPI application")
    app = FastAPI(
        title="Transcript Analysis API",
        description="API for analyzing text transcripts and providing summaries and action items",
        version="1.0.0",
        docs_url="/swagger",
        lifespan=lifespan,
    )
    
    # Register routes
    router = build_router(analyzer_service)
    app.include_router(router)
    logger.debug("Routes registered")
    
    # Add health check endpoint
    @app.get("/health", status_code=status.HTTP_200_OK, tags=["health"])
    def health_check():
        """Health check endpoint for monitoring and container health checks"""
        logger.debug("Health check endpoint called")
        return {"status": "healthy"}
    
    return app


app = create_app() 