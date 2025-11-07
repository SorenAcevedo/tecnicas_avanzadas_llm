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


settings = AppSettings()
