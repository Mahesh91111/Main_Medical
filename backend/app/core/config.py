from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the AI Medical Assistant backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "AI Medical Assistant & Clinical Intelligence Platform"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = Field(
        default="",
        description="PostgreSQL connection string; must be supplied via env/.env.",
    )

    JWT_SECRET_KEY: str = "dev-only-change-this-secret-before-deployment"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, gt=0)
    FRONTEND_ORIGINS: str = "http://localhost:5173"

    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4.1-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    PINECONE_API_KEY: str | None = None
    PINECONE_INDEX_NAME: str = "medical-documents"

    MAX_UPLOAD_SIZE_MB: int = Field(default=20, gt=0)
    ALLOWED_DOCUMENT_EXTENSIONS: str = ".pdf"
    LOG_LEVEL: str = "INFO"
    
    EMBEDDING_PROVIDER: str = "huggingface"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    PINECONE_API_KEY: str | None = None
    PINECONE_INDEX_NAME: str = "medical-documents"
    
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "openai/gpt-oss-20b"

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.FRONTEND_ORIGINS.split(",")
            if origin.strip()
        ]

    @property
    def allowed_document_extensions(self) -> list[str]:
        return [
            extension.strip().lower()
            for extension in self.ALLOWED_DOCUMENT_EXTENSIONS.split(",")
            if extension.strip()
        ]

    @model_validator(mode="after")
    def validate_production_settings(self):
        if self.APP_ENV.lower() == "production":
            if self.DEBUG:
                raise ValueError("DEBUG must be False in production.")

            if (
                self.JWT_SECRET_KEY
                == "dev-only-change-this-secret-before-deployment"
                or len(self.JWT_SECRET_KEY) < 32
            ):
                raise ValueError(
                    "Set a strong JWT_SECRET_KEY of at least 32 characters."
                )

            if not self.DATABASE_URL or "change_me" in self.DATABASE_URL:
                raise ValueError(
                    "Set DATABASE_URL to your production database credentials."
                )

        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
