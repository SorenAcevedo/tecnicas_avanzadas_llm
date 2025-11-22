import json
from pathlib import Path
from langchain.tools import tool
from difflib import SequenceMatcher

def string_similarity(a: str, b: str) -> float:
    """
    Calcula la similitud entre dos cadenas usando el algoritmo de ratio de secuencia.
    
    Args:
        a: Primera cadena
        b: Segunda cadena
        
    Returns:
        float: Valor entre 0 y 1 indicando la similitud (1 = idénticas)
    """
    return SequenceMatcher(None, a, b).ratio()

import json
from pathlib import Path
from langchain.tools import tool
from difflib import SequenceMatcher
from pydantic import BaseModel, Field

def string_similarity(a: str, b: str) -> float:
    """
    Calcula la similitud entre dos cadenas usando el algoritmo de ratio de secuencia.
    
    Args:
        a: Primera cadena.
        b: Segunda cadena.
        
    Returns:
        float: Valor entre 0 y 1 indicando la similitud (1 = idénticas).
    """
    return SequenceMatcher(None, a, b).ratio()

class FaqInput(BaseModel):
    """Esquema de entrada para la herramienta de búsqueda en preguntas frecuentes."""
    query: str = Field(..., description="La pregunta del usuario que se buscará en las FAQs.")

@tool
def faq_tool(faq_input: FaqInput) -> str:
    """
    Busca y recupera la respuesta a una pregunta frecuente (FAQ) desde un archivo JSON.

    Esta herramienta utiliza un algoritmo de coincidencia aproximada (fuzzy matching) para encontrar
    la pregunta más similar a la consulta del usuario en el archivo 'data/qa/faq.json'.
    Es ideal para responder preguntas generales sobre la empresa, productos o políticas.

    El proceso es el siguiente:
    1. Normaliza la pregunta del usuario (minúsculas, sin puntuación).
    2. Compara la pregunta normalizada con cada pregunta en el archivo de FAQs.
    3. Si encuentra una pregunta con un nivel de similitud superior a un umbral (60%),
       devuelve la respuesta correspondiente junto con el porcentaje de coincidencia.

    Args:
        faq_input (FaqInput): Un objeto que contiene la pregunta a buscar.
            - query (str): La pregunta del usuario.

    Returns:
        str: La respuesta a la pregunta más similar encontrada, con una indicación de la
             precisión de la coincidencia. Si no se encuentra ninguna coincidencia adecuada,
             devuelve un mensaje indicando que no se encontró una respuesta.
    """
    faq_path = Path(__file__).parent.parent.parent / "data" / "qa" / "faq.json"
    
    try:
        with open(faq_path, "r", encoding="utf-8") as f:
            faqs = json.load(f)
    except FileNotFoundError:
        return "Error: El archivo de preguntas frecuentes (faq.json) no se encontró."
    except json.JSONDecodeError:
        return "Error: No se pudo leer el archivo faq.json. Asegúrate de que sea un JSON válido."

    # Normalizar la query
    normalized_query = faq_input.query.lower().strip().replace("¿", "").replace("?", "").replace("¡", "").replace("!", "").replace(".", "")
    
    # Encontrar la pregunta más similar
    best_match = None
    best_score = 0
    threshold = 0.6  # Umbral mínimo de similitud
    
    for faq in faqs:
        normalized_question = faq["pregunta"].lower().strip().replace("¿", "").replace("?", "").replace("¡", "").replace("!", "").replace(".", "")
        score = string_similarity(normalized_question, normalized_query)
        
        if score > best_score:
            best_score = score
            best_match = faq
    
    if best_match and best_score >= threshold:
        return f"{best_match['respuesta']} (Coincidencia: {best_score:.2%})"
    
    return "Lo siento, no encontré una pregunta similar en las preguntas frecuentes."