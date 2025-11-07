"""
Ejemplo de configuración de tools para el chatbot.
Define herramientas personalizadas que el agente puede usar.
"""

from langchain.tools import tool
from typing import Optional
from src.tools.faq_tool import get_faq_answer

try:
    from src.retrieval.retriever import search as chroma_search
except Exception:  # pragma: no cover - defensive import for early stages
    chroma_search = None
@tool
def search_knowledge_base(query: str, top_k: int = 4, tipo: Optional[str] = None) -> str:
    """Busca información en la base vectorial (Chroma) y devuelve contexto relevante.

    Args:
        query: pregunta o texto a buscar.
        top_k: número de fragmentos a recuperar.
        tipo: filtro opcional por tipo de documento ("product" | "company").

    Returns:
        Texto concatenado con las mejores coincidencias.
    """
    if chroma_search is None:
        return "La búsqueda RAG aún no está disponible (módulo de retrieval no cargado)."
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

# Lista de todas las herramientas disponibles
AVAILABLE_TOOLS = [
    get_faq_answer,
    search_knowledge_base    
]


def get_tools():
    """
    Retorna la lista de herramientas configuradas para el agente.
    
    Returns:
        Lista de herramientas de LangChain.
    """
    return AVAILABLE_TOOLS
