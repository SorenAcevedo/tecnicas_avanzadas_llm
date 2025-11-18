"""
Configuración base para variables de entorno del proyecto.
"""

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    LOG_LEVEL: str = "DEBUG"
    OLLAMA_API_URL: str = "http://localhost:11434"
    DEFAULT_COLLECTION: str = "colgate_palmolive_kb_gemini_full"
    VECTOR_DB_PATH: str = "./data/vector_db"
    GOOGLE_API_KEY: str
    DB_URI: str
    
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8001

    # SMTP Configuration for sending emails
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_SENDER_EMAIL: str


settings = AppSettings()
