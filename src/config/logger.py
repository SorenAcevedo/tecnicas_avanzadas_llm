"""
Logger centralizado para el proyecto.
Provee funciones para obtener loggers configurados según el nivel definido en las variables de entorno.
"""
import logging
from src.config.settings import settings

def get_logger(name=None):
    """
    Obtiene un logger configurado con el nivel global.
    Args:
        name (str, opcional): Nombre del logger. Si no se especifica, usa 'root'.
    Returns:
        logging.Logger: Logger configurado.
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s', '%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
