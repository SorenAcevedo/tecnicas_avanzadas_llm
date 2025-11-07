"""
Chroma vector store management.
Mantiene una instancia en caché por colección/ruta para evitar reabrir el store por cada consulta.
"""

import os
from pathlib import Path
from typing import Optional, Tuple, Dict

from langchain_chroma import Chroma

from src.config.settings import settings
from .embeddings import get_embeddings


# Cachés en memoria del proceso para evitar recrear objetos por consulta
_EMBEDDINGS_SINGLETON = None
_CHROMA_CACHE: Dict[Tuple[str, str], Chroma] = {}


def _get_embeddings_cached():
    global _EMBEDDINGS_SINGLETON
    if _EMBEDDINGS_SINGLETON is None:
        _EMBEDDINGS_SINGLETON = get_embeddings()
    return _EMBEDDINGS_SINGLETON


def get_chroma(
    collection: Optional[str] = None, persist_dir: Optional[str] = None
) -> Chroma:
    """Open or create a Chroma collection with persistence.

    Args:
        collection: Name of the Chroma collection.
        persist_dir: Directory path to store Chroma data.

    Returns:
        Chroma instance connected to the persistent collection.
    """
    collection = collection or DEFAULT_COLLECTION
    persist_dir = persist_dir or DEFAULT_PERSIST_DIR
    Path(persist_dir).mkdir(parents=True, exist_ok=True)

    key = (collection, persist_dir)
    if key in _CHROMA_CACHE:
        return _CHROMA_CACHE[key]

    embeddings = _get_embeddings_cached()
    store = Chroma(
        collection_name=collection,
        embedding_function=embeddings,
        host="localhost",
        port=8000,
        ssl=False
    )
    _CHROMA_CACHE[key] = store
    return store


def preload_vector_store(
    collection: Optional[str] = None, persist_dir: Optional[str] = None
) -> None:
    """Inicializa en memoria el vector store por defecto para esta sesión de proceso."""
    get_chroma(collection=collection, persist_dir=persist_dir)
