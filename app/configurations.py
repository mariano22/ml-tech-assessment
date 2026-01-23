import pydantic_settings
from app.logging import get_logger

# Create a logger for this module
logger = get_logger(__name__)


class EnvConfigs(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-2024-08-06"
    # Add LOG_LEVEL with a default
    LOG_LEVEL: str = "INFO"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.debug(f"Environment configuration loaded with model: {self.OPENAI_MODEL}")
        # Don't log the API key for security reasons, just log if it's set
        logger.debug(f"OpenAI API key {'is set' if self.OPENAI_API_KEY else 'is NOT set'}")


