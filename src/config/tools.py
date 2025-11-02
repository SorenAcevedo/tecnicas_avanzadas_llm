"""
Ejemplo de configuración de tools para el chatbot.
Define herramientas personalizadas que el agente puede usar.
"""

from langchain.tools import tool
from typing import Optional


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
]


def get_tools():
    """
    Retorna la lista de herramientas configuradas para el agente.
    
    Returns:
        Lista de herramientas de LangChain.
    """
    return AVAILABLE_TOOLS
