from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from braintrust import init_logger


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # API Keys
    GEMINI_API_KEY: str
    EXA_API_KEY: str

    BRAINTRUST_API_KEY: str

    # Exa Search Settings
    EXA_MAX_RESULTS: int = 5  # default value
    EXA_USE_HYBRID_SEARCH: bool = False
    EXA_NEURAL_RATIO: float = 1.0

    # LiteLLM/Gemini Settings
    GEMINI_MODEL: str
    GEMINI_MAX_TOKENS: int = 1000  # default value

    # Logging
    LOG_LEVEL: str = "INFO"  # default value

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        init_logger(project="HasAnyone")
        # Validate required environment variables
        if not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY must be set in environment variables")
        if not self.EXA_API_KEY:
            raise ValueError("EXA_API_KEY must be set in environment variables")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings"""
    return Settings()
