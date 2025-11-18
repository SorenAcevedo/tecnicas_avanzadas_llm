from src.tools.faq_tool import get_faq_answer
from src.tools.retrieve_tool import search_knowledge_base
from src.tools.price_tool import get_product_prices
from src.tools.calculator_tool import calculator_tool
from src.tools.pdf_quote_tool import pdf_quote_tool
from src.tools.email_quote_tool import email_quote_tool

AVAILABLE_TOOLS = [
    get_faq_answer,
    search_knowledge_base,
    get_product_prices,
    calculator_tool,
    pdf_quote_tool,
    email_quote_tool,
]


def get_tools():
    """
    Retorna la lista de herramientas configuradas para el agente.

    Returns:
        Lista de herramientas de LangChain.
    """
    return AVAILABLE_TOOLS
