"""
Herramienta de búsqueda con base de datos vectorial para LangChain.
"""

from typing import Optional
from langchain.tools import tool

from src.retrieval.retriever import search as chroma_search


"""
Herramienta de búsqueda con base de datos vectorial para LangChain.
"""

from typing import Optional
from langchain.tools import tool
from pydantic import BaseModel, Field

from src.retrieval.retriever import search as chroma_search

class RetrieveInput(BaseModel):
    """Esquema de entrada para la herramienta de búsqueda en la base de conocimiento."""
    query: str = Field(..., description="La pregunta o texto a buscar en la base de datos vectorial.")
    top_k: int = Field(4, description="El número de fragmentos de texto más relevantes a recuperar.")
    filter_type: Optional[str] = Field(None, description="Un filtro opcional para limitar la búsqueda a un tipo de documento específico. Valores válidos: 'product', 'company'.")

@tool
def retrieve_tool(retrieve_input: RetrieveInput) -> str:
    """
    Busca información en la base de conocimiento vectorial (ChromaDB) para obtener contexto relevante.

    Esta herramienta es fundamental para el sistema de RAG (Retrieval-Augmented Generation).
    Realiza una búsqueda semántica en una base de datos vectorial (ChromaDB) para encontrar
    fragmentos de texto que sean relevantes para la consulta del usuario. Puede filtrar
    la búsqueda por tipo de documento si se especifica.

    El proceso es el siguiente:
    1. Recibe una consulta (query) y parámetros opcionales (top_k, filter_type).
    2. Llama a la función de búsqueda del retriever, que consulta ChromaDB.
    3. Recopila los fragmentos de texto más relevantes.
    4. Formatea los resultados, incluyendo el texto del fragmento, su tipo y su fuente,
       y los devuelve como una única cadena de texto.

    Args:
        retrieve_input (RetrieveInput): Un objeto que contiene los parámetros de búsqueda.
            - query (str): La pregunta o texto a buscar.
            - top_k (int): El número máximo de resultados a devolver.
            - filter_type (Optional[str]): Filtro para acotar la búsqueda por tipo de
              documento ('product' o 'company').

    Returns:
        str: Una cadena de texto que concatena los fragmentos de información más
             relevantes encontrados, listos para ser usados en la generación de una
             respuesta. Si no se encuentran resultados o hay un error, devuelve un
             mensaje informativo.
    """
    if chroma_search is None:
        return "La búsqueda RAG aún no está disponible (módulo de retrieval no cargado)."
    
    try:
        results = chroma_search(
            query=retrieve_input.query,
            top_k=retrieve_input.top_k,
            filter_type=retrieve_input.filter_type
        )
        if not results:
            return "No se encontraron resultados relevantes en la base de conocimiento para la consulta."
        
        lines = []
        for r in results:
            metadata = r.get("metadata", {})
            source = metadata.get("source", "desconocida")
            doc_type = metadata.get("type", "desconocido")
            content = r.get("text", "")
            lines.append(f"[Tipo: {doc_type}] {content}\n(Fuente: {source})")
            
        return "\n\n---\n\n".join(lines)
    except Exception as e:
        # En un entorno de producción, aquí se registraría el error.
        return f"Error al consultar la base de conocimiento: {e}"
