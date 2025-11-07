"""
Herramienta de búsqueda con base de datos vectorial para LangChain.
"""

from typing import Optional
from langchain.tools import tool

from src.retrieval.retriever import search as chroma_search


@tool
def search_knowledge_base(
    query: str, top_k: int = 4, tipo: Optional[str] = None
) -> str:
    """Busca información en la base vectorial (Chroma) y devuelve contexto relevante.

    Args:
        query: pregunta o texto a buscar.
        top_k: número de fragmentos a recuperar.
        tipo: filtro opcional por tipo de documento ("product" | "company").

    Returns:
        Texto concatenado con las mejores coincidencias.
    """
    if chroma_search is None:
        return (
            "La búsqueda RAG aún no está disponible (módulo de retrieval no cargado)."
        )
    try:
        results = chroma_search(query=query, top_k=top_k, filter_type=tipo)
        if not results:
            return "Sin resultados relevantes en la base de conocimiento."
        lines = []
        for r in results:
            meta = r.get("metadata", {})
            src = meta.get("source", "")
            t = meta.get("type", "")
            lines.append(f"[tipo={t}] {r['text']}\n(fuente: {src})")
        return "\n\n".join(lines)
    except Exception as e:
        return f"Error al consultar la base vectorial: {e}"
