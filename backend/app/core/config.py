from pydantic_settings import BaseSettings, SettingsConfigDict


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

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()