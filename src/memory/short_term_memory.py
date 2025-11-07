"""
Utilidades para la gestión de memoria a corto plazo con checkpointer Postgres y generación de thread_id único.
"""

import uuid

from langgraph.checkpoint.postgres import PostgresSaver

from src.config.settings import settings


def create_checkpointer_context():
    """Crea el context manager del checkpointer."""
    return PostgresSaver.from_conn_string(settings.DB_URI)


def generate_thread_id() -> str:
    """Genera un identificador único de conversación (thread_id)."""
    return str(uuid.uuid4())
