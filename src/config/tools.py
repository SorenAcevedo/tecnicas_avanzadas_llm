"""
Ejemplo de configuración de tools para el chatbot.
Define herramientas personalizadas que el agente puede usar.
"""

from langchain.tools import tool
from typing import Optional

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


@tool
def buscar_producto(nombre: str) -> str:
    """
    Busca información sobre un producto específico de Colgate Palmolive.
    
    Args:
        nombre: Nombre o categoría del producto a buscar.
        
    Returns:
        Información del producto encontrado.
    """
    # TODO: Implementar búsqueda real en base de datos o archivos
    return f"Información del producto: {nombre}"


@tool
def obtener_horarios(sede: Optional[str] = None) -> str:
    """
    Obtiene los horarios de atención de Colgate Palmolive.
    
    Args:
        sede: Nombre de la sede (opcional). Si no se especifica, devuelve horarios generales.
        
    Returns:
        Horarios de atención.
    """
    # TODO: Implementar consulta real de horarios
    if sede:
        return f"Horarios de la sede {sede}: Lunes a Viernes 8:00 AM - 6:00 PM"
    return "Horarios generales: Lunes a Viernes 8:00 AM - 6:00 PM"


@tool
def obtener_contacto(tipo: str = "general") -> str:
    """
    Obtiene información de contacto de Colgate Palmolive.
    
    Args:
        tipo: Tipo de contacto (general, ventas, soporte, etc.)
        
    Returns:
        Información de contacto.
    """
    # TODO: Implementar consulta real de contactos
    contactos = {
        "general": "📞 Teléfono: 01-800-COLGATE | 📧 Email: contacto@colgate.com",
        "ventas": "📞 Teléfono: 01-800-VENTAS | 📧 Email: ventas@colgate.com",
        "soporte": "📞 Teléfono: 01-800-SOPORTE | 📧 Email: soporte@colgate.com",
    }
    return contactos.get(tipo.lower(), contactos["general"])


# Lista de todas las herramientas disponibles
AVAILABLE_TOOLS = [
    buscar_producto,
    obtener_horarios,
    obtener_contacto,
    search_knowledge_base,
]


def get_tools():
    """
    Retorna la lista de herramientas configuradas para el agente.
    
    Returns:
        Lista de herramientas de LangChain.
    """
    return AVAILABLE_TOOLS
