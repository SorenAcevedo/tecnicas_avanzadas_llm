"""
Herramienta para consultar precios de productos Colgate y Palmolive.
Permite buscar productos y ver precios en diferentes tiendas.
"""

import json
from pathlib import Path
from langchain.tools import tool
from difflib import SequenceMatcher
from typing import Optional


def string_similarity(a: str, b: str) -> float:
    """
    Calcula la similitud entre dos cadenas usando el algoritmo de ratio de secuencia.
    
    Args:
        a: Primera cadena
        b: Segunda cadena
        
    Returns:
        float: Valor entre 0 y 1 indicando la similitud (1 = idénticas)
    """
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def load_prices_data():
    """
    Carga el archivo JSON de precios.
    
    Returns:
        dict: Diccionario con los datos de precios o None si hay error
    """
    prices_path = Path(__file__).parent.parent.parent / "data" / "qa" / "prices.json"
    
    try:
        with open(prices_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None


def format_price_info(producto: dict, show_all_stores: bool = True) -> str:
    """
    Formatea la información de precios de un producto de manera legible.
    
    Args:
        producto: Diccionario con información del producto
        show_all_stores: Si mostrar todas las tiendas o solo las disponibles
        
    Returns:
        str: Información formateada del producto y sus precios
    """
    lines = []
    lines.append(f"Producto: {producto['nombre']}")
    lines.append(f"Marca: {producto['marca']}")
    
    if producto['sku']:
        lines.append(f"SKU: {producto['sku']}")
    
    lines.append("")
    
    # Información de disponibilidad
    if producto['tiendas_disponibles'] > 0:
        lines.append(f"Disponible en {producto['tiendas_disponibles']} tienda(s)")
    if producto['tiendas_agotadas'] > 0:
        lines.append(f"Agotado en {producto['tiendas_agotadas']} tienda(s)")
    
    lines.append("")
    
    # Precios por tienda
    tiendas_a_mostrar = producto['precios_por_tienda']
    if not show_all_stores:
        tiendas_a_mostrar = [t for t in tiendas_a_mostrar if t['disponibilidad'] == 'Disponible']
    
    if tiendas_a_mostrar:
        lines.append("Precios por tienda:")
        for tienda in sorted(tiendas_a_mostrar, key=lambda x: x['precio'] if x['precio'] else float('inf')):
            disponibilidad = "Disponible" if tienda['disponibilidad'] == 'Disponible' else "Agotado"
            precio_text = tienda['precio_formateado']
            lines.append(f"  - {tienda['tienda']}: {precio_text} ({disponibilidad})")
    
    lines.append("")
    
    # Estadísticas de precios (solo si hay precios válidos)
    if producto['precio_minimo'] is not None:
        lines.append("Resumen de precios:")
        lines.append(f"  - Precio minimo: {producto['precio_minimo_formateado']}")
        lines.append(f"  - Precio maximo: {producto['precio_maximo_formateado']}")
        lines.append(f"  - Precio promedio: {producto['precio_promedio_formateado']}")
        
        # Identificar mejor oferta
        mejor_tienda = min(
            [t for t in producto['precios_por_tienda'] if t['precio'] and t['disponibilidad'] == 'Disponible'],
            key=lambda x: x['precio'],
            default=None
        )
        
        if mejor_tienda:
            lines.append("")
            lines.append(f"Mejor oferta: {mejor_tienda['precio_formateado']} en {mejor_tienda['tienda']}")
    else:
        lines.append("No hay informacion de precios disponible para este producto.")
    
    return "\n".join(lines)


"""
Herramienta para consultar precios de productos Colgate y Palmolive.
Permite buscar productos y ver precios en diferentes tiendas.
"""

import json
from pathlib import Path
from langchain.tools import tool
from difflib import SequenceMatcher
from typing import Optional
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
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def load_prices_data():
    """
    Carga el archivo JSON de precios.
    
    Returns:
        dict: Diccionario con los datos de precios o None si hay error.
    """
    prices_path = Path(__file__).parent.parent.parent / "data" / "qa" / "prices.json"
    
    try:
        with open(prices_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def format_price_info(producto: dict) -> str:
    """
    Formatea la información de precios de un producto de manera legible.
    
    Args:
        producto: Diccionario con información del producto.
        
    Returns:
        str: Información formateada del producto y sus precios.
    """
    lines = [
        f"Producto: {producto['nombre']}",
        f"Marca: {producto['marca']}",
    ]
    if producto.get('sku'):
        lines.append(f"SKU: {producto['sku']}")
    lines.append("")

    tiendas_disponibles = sum(1 for t in producto['precios_por_tienda'] if t.get('disponibilidad') == 'Disponible')
    tiendas_agotadas = len(producto['precios_por_tienda']) - tiendas_disponibles
    
    if tiendas_disponibles > 0:
        lines.append(f"Disponible en {tiendas_disponibles} tienda(s)")
    if tiendas_agotadas > 0:
        lines.append(f"Agotado en {tiendas_agotadas} tienda(s)")
    lines.append("")

    if producto['precios_por_tienda']:
        lines.append("Precios por tienda:")
        for tienda in sorted(producto['precios_por_tienda'], key=lambda x: x.get('precio') or float('inf')):
            disponibilidad = "Disponible" if tienda.get('disponibilidad') == 'Disponible' else "Agotado"
            precio_text = tienda.get('precio_formateado', 'N/A')
            lines.append(f"  - {tienda['tienda']}: {precio_text} ({disponibilidad})")
    lines.append("")

    precios_validos = [t['precio'] for t in producto['precios_por_tienda'] if t.get('precio') and t.get('disponibilidad') == 'Disponible']
    if precios_validos:
        precio_minimo = min(precios_validos)
        mejor_tienda = min([t for t in producto['precios_por_tienda'] if t.get('precio') == precio_minimo], key=lambda x: x['tienda'])

        lines.append("Resumen de precios:")
        lines.append(f"  - Precio mínimo: ${min(precios_validos):,.2f}")
        lines.append(f"  - Precio máximo: ${max(precios_validos):,.2f}")
        lines.append(f"  - Precio promedio: ${sum(precios_validos) / len(precios_validos):,.2f}")
        lines.append("")
        lines.append(f"Mejor oferta: ${mejor_tienda['precio']:,.2f} en {mejor_tienda['tienda']}")
    else:
        lines.append("No hay información de precios disponible para este producto en las tiendas seleccionadas.")
    
    return "\n".join(lines)

class PriceInput(BaseModel):
    """Esquema de entrada para la herramienta de consulta de precios."""
    query: str = Field(..., description="Nombre del producto a buscar (ej: 'crema dental colgate', 'jabón palmolive').")
    store: Optional[str] = Field(None, description="Nombre específico de una tienda para filtrar los resultados (ej: 'ExitoCO', 'JumboCO').")

@tool
def price_tool(price_input: PriceInput) -> str:
    """
    Busca información de precios de un producto en una o varias tiendas.

    Esta herramienta consulta una base de datos local (prices.json) para encontrar información
    detallada sobre el precio de un producto. Utiliza coincidencia aproximada para encontrar
    el producto más relevante según la consulta del usuario. Opcionalmente, puede filtrar
    los resultados para una tienda específica.

    El proceso es el siguiente:
    1. Carga los datos de precios desde 'data/qa/prices.json'.
    2. Busca el producto que mejor coincida con la `query` del usuario.
    3. Si se especifica una `store`, filtra los precios para mostrar solo esa tienda.
    4. Formatea y devuelve un resumen completo con el nombre del producto, marca, SKU,
       disponibilidad, precios por tienda y estadísticas de precios (mínimo, máximo, promedio).

    Args:
        price_input (PriceInput): Un objeto que contiene los parámetros de búsqueda.
            - query (str): El nombre del producto a buscar.
            - store (Optional[str]): El nombre de la tienda para filtrar la búsqueda.

    Returns:
        str: Una cadena de texto con la información detallada de precios del producto
             encontrado, o un mensaje de error si no se encuentra el producto o el archivo
             de datos no está disponible.
    """
    prices_data = load_prices_data()
    if prices_data is None:
        return "Error: No se pudo cargar la base de datos de precios. Asegúrate de que el archivo prices.json existe y es válido."
    
    productos = prices_data.get('productos', [])
    if not productos:
        return "Error: No hay productos en la base de datos de precios."
    
    normalized_query = price_input.query.lower().strip()
    
    best_match = None
    best_score = 0.0
    threshold = 0.4
    
    for producto in productos:
        nombre_score = string_similarity(producto.get('nombre', '').lower(), normalized_query)
        marca_score = string_similarity(f"{producto.get('marca', '')} {producto.get('nombre', '')}".lower(), normalized_query)
        score = max(nombre_score, marca_score)
        
        if score > best_score:
            best_score = score
            best_match = producto
            
    if not best_match or best_score < threshold:
        return f"No encontré un producto que coincida con '{price_input.query}'. Intenta ser más específico."

    found_product = best_match.copy()
    
    if price_input.store:
        tienda_normalizada = price_input.store.strip().lower()
        precios_filtrados = [
            t for t in found_product.get('precios_por_tienda', [])
            if tienda_normalizada in t.get('tienda', '').lower()
        ]
        
        if not precios_filtrados:
            return f"No encontré información de precios para '{found_product['nombre']}' en la tienda '{price_input.store}'."
        
        found_product['precios_por_tienda'] = precios_filtrados

    result = format_price_info(found_product)
    
    if best_score < 0.9:
        result = f"Encontrado con {best_score:.0%} de similitud:\n\n{result}"
        
    return result
