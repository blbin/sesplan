from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DOMAIN: str

    # LangChain / Google AI Configuration
    GOOGLE_API_KEY: str
    GEMINI_MODEL_NAME: str = "gemini-2.0-flash"

    class Config:
        # Pokud používáte .env soubor, Pydantic ho automaticky načte
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()

