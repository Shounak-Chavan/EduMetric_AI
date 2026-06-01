from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    APP_NAME: str = "EduMetric"

    DATABASE_URL: str

    SUPABASE_URL: str
    SUPABASE_PUBLISHABLE_KEY: str
    SUPABASE_SECRET_KEY: str

    GEMINI_API_KEY: str
    GROQ_API_KEY: str

    RESEND_API_KEY: str
    FROM_EMAIL: str

    REDIS_URL: str

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    FRONTEND_URL: str

    SUPER_ADMIN_NAME: str
    SUPER_ADMIN_EMAIL: str
    SUPER_ADMIN_PASSWORD: str

    AUTH_COOKIE_NAME: str = "edumetric_jwt"
    AUTH_COOKIE_SECURE: bool = False
    AUTH_COOKIE_SAMESITE: str = "lax"
    AUTH_COOKIE_MAX_AGE_SECONDS: int = 3600

    @field_validator("AUTH_COOKIE_SAMESITE")
    @classmethod
    def validate_cookie_samesite(cls, value: str) -> str:
        normalized = value.lower().strip()
        if normalized not in {"lax", "strict", "none"}:
            raise ValueError(
                "AUTH_COOKIE_SAMESITE must be one of: lax, strict, none"
            )
        return normalized

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()