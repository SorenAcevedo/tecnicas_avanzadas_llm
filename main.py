"""
Módulo principal para iniciar la aplicación FastAPI.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Importación de configuraciones
from src.config.settings import settings
from src.config.logger import get_logger

# Importación de rutas
from src.api.routes import router

# Configuración de logging
logger = get_logger(__name__)

# Creación de la app
app = FastAPI(
    title="Colgate LLM API",
    description="API para interactuar con el modelo de lenguaje de Colgate utilizando FastAPI.",
    version="1.0.0",
)

# Configuración de CORS desde settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusión de routers
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """
    Endpoint de salud para verificar que la API está funcionando.
    """
    return {"status": "ok", "message": "API running"}


@app.get("/health")
async def health_check():
    """
    Endpoint de comprobación de salud para monitoreo.
    """
    return {
        "status": "ok",
        "version": app.version,
        "environment": settings.ENVIRONMENT,
    }


if __name__ == "__main__":
    import uvicorn

    # Si se ejecuta directamente, iniciar con uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
