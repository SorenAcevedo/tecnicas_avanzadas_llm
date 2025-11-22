from src.tools.faq_tool import faq_tool
from src.tools.retrieve_tool import retrieve_tool
from src.tools.price_tool import price_tool
from src.tools.calculator_tool import calculator_tool
from src.tools.pdf_quote_tool import pdf_quote_tool
from src.tools.email_quote_tool import email_quote_tool

AVAILABLE_TOOLS = [
    faq_tool,
    retrieve_tool,
    price_tool,
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
