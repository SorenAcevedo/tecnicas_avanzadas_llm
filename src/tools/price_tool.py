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


@tool
def get_product_prices(query: str, tienda: Optional[str] = None) -> str:
    """
    Busca información de precios de un producto en diferentes tiendas.
    Usa coincidencia aproximada para encontrar el producto más similar.
    
    Args:
        query: Nombre del producto a buscar (ej: "crema dental colgate", "jabón palmolive")
        tienda: (Opcional) Nombre específico de tienda para filtrar (ej: "ExitoCO", "JumboCO")
    
    Returns:
        str: Información detallada de precios del producto encontrado, o mensaje de error
    
    Examples:
        >>> get_product_prices("crema dental colgate total")
        >>> get_product_prices("jabón líquido palmolive", "ExitoCO")
    """
    # Cargar datos de precios
    prices_data = load_prices_data()
    
    if prices_data is None:
        return "Error: No se pudo cargar la base de datos de precios. Asegurate de que el archivo prices.json existe."
    
    productos = prices_data.get('productos', [])
    
    if not productos:
        return "Error: No hay productos en la base de datos de precios."
    
    # Normalizar query
    normalized_query = query.lower().strip()
    
    # Buscar el producto más similar
    best_match = None
    best_score = 0
    threshold = 0.4  # Umbral más bajo que FAQ para ser más flexible con nombres de productos
    
    for producto in productos:
        # Comparar con el nombre del producto
        nombre_score = string_similarity(producto['nombre'].lower(), normalized_query)
        
        # También comparar con marca + nombre
        nombre_completo = f"{producto['marca']} {producto['nombre']}".lower()
        marca_score = string_similarity(nombre_completo, normalized_query)
        
        # Tomar el mejor score
        score = max(nombre_score, marca_score)
        
        if score > best_score:
            best_score = score
            best_match = producto
    
    # Verificar si encontramos un match válido
    if not best_match or best_score < threshold:
        return f"No encontre un producto que coincida con '{query}'. Intenta ser mas especifico o usa palabras clave como 'Colgate', 'Palmolive', 'crema dental', 'jabon', etc."
    
    # Filtrar por tienda si se especificó
    if tienda:
        tienda_normalizada = tienda.strip()
        producto_filtrado = best_match.copy()
        producto_filtrado['precios_por_tienda'] = [
            t for t in best_match['precios_por_tienda']
            if tienda_normalizada.lower() in t['tienda'].lower()
        ]
        
        if not producto_filtrado['precios_por_tienda']:
            return f"No encontre informacion de precios para '{best_match['nombre']}' en la tienda '{tienda}'."
        
        # Recalcular estadísticas para la tienda específica
        precios_validos = [t['precio'] for t in producto_filtrado['precios_por_tienda'] if t['precio']]
        if precios_validos:
            producto_filtrado['precio_minimo'] = min(precios_validos)
            producto_filtrado['precio_maximo'] = max(precios_validos)
            producto_filtrado['precio_promedio'] = sum(precios_validos) / len(precios_validos)
        
        best_match = producto_filtrado
    
    # Formatear y retornar información
    result = format_price_info(best_match)
    
    # Agregar nota de coincidencia si no es perfecta
    if best_score < 0.9:
        similitud_porcentaje = int(best_score * 100)
        result = f"Encontrado con {similitud_porcentaje}% de similitud:\n\n{result}"
    
    return result
