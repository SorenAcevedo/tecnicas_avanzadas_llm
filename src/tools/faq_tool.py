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

@tool
def get_faq_answer(query: str) -> str:
    """
    Busca y recupera la respuesta a una pregunta frecuente del archivo faq.json.
    Usa coincidencia aproximada para encontrar la pregunta más similar.

    Args:
        query (str): La pregunta a buscar.

    Returns:
        str: La respuesta a la pregunta más similar, o un mensaje indicando que no se encontró.
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
    normalized_query = query.lower().strip().replace("¿", "").replace("?", "").replace("¡", "").replace("!", "").replace(".", "")
    
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