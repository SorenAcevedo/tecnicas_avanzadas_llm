"""
Configuración base para variables de entorno del proyecto.
"""

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    LOG_LEVEL: str = "DEBUG"
    OLLAMA_API_URL: str = "http://localhost:11434"
    OPENAI_API_KEY: str = "your_openai_api_key_here"
    GEMINI_API_KEY: str = "your_gemini_api_key_here"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = AppSettings()
