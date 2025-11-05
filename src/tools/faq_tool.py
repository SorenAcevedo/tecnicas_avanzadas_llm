import json
from pathlib import Path
from langchain.tools import tool

@tool
def get_faq_answer(query: str) -> str:
    """
    Busca y recupera la respuesta a una pregunta frecuente del archivo faq.json.
    La búsqueda es precisa y determinista, buscando coincidencias exactas (ignorando mayúsculas/minúsculas y puntuación).

    Args:
        query (str): La pregunta a buscar.

    Returns:
        str: La respuesta a la pregunta, o un mensaje indicando que no se encontró.
    """
    faq_path = Path(__file__).parent.parent.parent / "data" / "qa" / "faq.json"
    
    try:
        with open(faq_path, "r", encoding="utf-8") as f:
            faqs = json.load(f)
    except FileNotFoundError:
        return "Error: El archivo de preguntas frecuentes (faq.json) no se encontró."
    except json.JSONDecodeError:
        return "Error: No se pudo leer el archivo faq.json. Asegúrate de que sea un JSON válido."

    # Normalizar la query para una búsqueda precisa
    normalized_query = query.lower().strip().replace("¿", "").replace("?", "").replace("¡", "").replace("!", "").replace(".", "")

    for faq in faqs:
        normalized_question = faq["pregunta"].lower().strip().replace("¿", "").replace("?", "").replace("¡", "").replace("!", "").replace(".", "")
        if normalized_question == normalized_query:
            return faq["respuesta"]
    
    return "Lo siento, no encontré una respuesta exacta a tu pregunta en las preguntas frecuentes."