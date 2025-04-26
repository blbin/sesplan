from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DOMAIN: str

    # LangChain / Google AI Configuration
    GOOGLE_API_KEY: str
    GEMINI_MODEL_NAME: str

    # Redis for Rate Limiter
    REDIS_URL: str

    # Rate Limits (per user)
    # Spojeno středníkem pro aplikaci více limitů najednou
    AI_REQUEST_LIMITS: str

    # Obecné Rate Limits (prevence spamu/útoků)
    AUTH_LOGIN_LIMIT: str
    USER_REGISTER_LIMIT: str
    GENERIC_READ_LIMIT: str
    GENERIC_WRITE_LIMIT: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()

