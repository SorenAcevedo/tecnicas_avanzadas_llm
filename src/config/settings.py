"""
Configuración base para variables de entorno del proyecto.
"""

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    LOG_LEVEL: str = "DEBUG"
    OLLAMA_API_URL: str = "http://localhost:11434"
    OPENAI_API_KEY: str
    GOOGLE_API_KEY: str
    DB_URI: str


settings = AppSettings()
