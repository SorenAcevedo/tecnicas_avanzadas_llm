from src.tools.faq_tool import get_faq_answer
from src.tools.retrieve_tool import search_knowledge_base

AVAILABLE_TOOLS = [get_faq_answer, search_knowledge_base]


def get_tools():
    """
    Retorna la lista de herramientas configuradas para el agente.

    Returns:
        Lista de herramientas de LangChain.
    """
    return AVAILABLE_TOOLS
