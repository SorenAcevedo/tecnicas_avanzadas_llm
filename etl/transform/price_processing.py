"""
Script para extraer y consolidar información de precios de productos Colgate y Palmolive.
Genera un archivo JSON con precios estructurados para consultas rápidas.
"""

import pandas as pd
import json
import ast
import os
from pathlib import Path


def parse_tiendas(tiendas_str):
    """
    Parsea la columna 'tiendas' que viene como string de lista JSON.
    
    Args:
        tiendas_str: String con formato de lista JSON
        
    Returns:
        Lista de diccionarios con información de tiendas, o lista vacía si hay error
    """
    if pd.isna(tiendas_str) or tiendas_str == '':
        return []
    
    try:
        # Intentar evaluar como literal de Python
        tiendas = ast.literal_eval(tiendas_str)
        return tiendas if isinstance(tiendas, list) else []
    except (ValueError, SyntaxError):
        return []


def parse_price(price_str):
    """
    Convierte string de precio a float.
    
    Args:
        price_str: String con formato de precio (ej: "14.062,00" o "N/A")
        
    Returns:
        Float del precio o None si no es válido
    """
    if not price_str or price_str == 'N/A':
        return None
    
    try:
        # Remover puntos de miles y reemplazar coma por punto
        cleaned = str(price_str).replace('.', '').replace(',', '.')
        return float(cleaned)
    except (ValueError, AttributeError):
        return None


def format_price(price):
    """
    Formatea un precio como string legible.
    
    Args:
        price: Float del precio
        
    Returns:
        String formateado (ej: "$14.062")
    """
    if price is None:
        return "N/A"
    return f"${price:,.0f}".replace(',', '.')


def process_product_prices(row, marca):
    """
    Procesa una fila de producto y extrae información de precios.
    
    Args:
        row: Fila de DataFrame
        marca: Marca del producto (Colgate o Palmolive)
        
    Returns:
        Diccionario con información estructurada del producto y precios
    """
    tiendas = parse_tiendas(row.get('tiendas', '[]'))
    
    precios_validos = []
    precios_por_tienda = []
    tiendas_disponibles = 0
    tiendas_agotadas = 0
    
    for tienda_info in tiendas:
        precio_num = parse_price(tienda_info.get('precio'))
        disponibilidad = tienda_info.get('disponibilidad', 'Desconocido')
        
        tienda_data = {
            'tienda': tienda_info.get('tienda', 'Desconocida'),
            'disponibilidad': disponibilidad,
            'precio': precio_num,
            'precio_formateado': format_price(precio_num)
        }
        
        precios_por_tienda.append(tienda_data)
        
        if disponibilidad == 'Disponible':
            tiendas_disponibles += 1
            if precio_num is not None:
                precios_validos.append(precio_num)
        else:
            tiendas_agotadas += 1
    
    # Calcular estadísticas de precios
    precio_minimo = min(precios_validos) if precios_validos else None
    precio_maximo = max(precios_validos) if precios_validos else None
    precio_promedio = sum(precios_validos) / len(precios_validos) if precios_validos else None
    
    return {
        'nombre': row.get('nombre', 'Sin nombre'),
        'sku': str(row.get('sku', '')),
        'marca': marca,
        'categoria': row.get('categoria', 'Sin categoría') if marca == 'Colgate' else 'Cuidado Personal',
        'precios_por_tienda': precios_por_tienda,
        'precio_minimo': precio_minimo,
        'precio_maximo': precio_maximo,
        'precio_promedio': precio_promedio,
        'precio_minimo_formateado': format_price(precio_minimo),
        'precio_maximo_formateado': format_price(precio_maximo),
        'precio_promedio_formateado': format_price(precio_promedio),
        'tiendas_disponibles': tiendas_disponibles,
        'tiendas_agotadas': tiendas_agotadas,
        'total_tiendas': len(tiendas)
    }


def main():
    """
    Procesa los CSVs de productos y genera el archivo JSON consolidado de precios.
    """
    # Obtener rutas
    base_dir = Path(__file__).parent.parent.parent
    raw_dir = base_dir / 'data' / 'raw'
    qa_dir = base_dir / 'data' / 'qa'
    
    # Crear directorio qa si no existe
    qa_dir.mkdir(parents=True, exist_ok=True)
    
    productos_con_precios = []
    
    # Procesar productos Colgate
    colgate_path = raw_dir / 'productos_colgate.csv'
    if colgate_path.exists():
        print(f"Procesando productos Colgate desde {colgate_path}...")
        df_colgate = pd.read_csv(colgate_path)
        for _, row in df_colgate.iterrows():
            producto = process_product_prices(row, 'Colgate')
            # Solo agregar si tiene al menos una tienda
            if producto['total_tiendas'] > 0:
                productos_con_precios.append(producto)
        print(f"✓ Procesados {len(df_colgate)} productos Colgate")
    else:
        print(f"⚠ No se encontró {colgate_path}")
    
    # Procesar productos Palmolive
    palmolive_path = raw_dir / 'productos_palmolive.csv'
    if palmolive_path.exists():
        print(f"Procesando productos Palmolive desde {palmolive_path}...")
        df_palmolive = pd.read_csv(palmolive_path)
        for _, row in df_palmolive.iterrows():
            producto = process_product_prices(row, 'Palmolive')
            # Solo agregar si tiene al menos una tienda
            if producto['total_tiendas'] > 0:
                productos_con_precios.append(producto)
        print(f"✓ Procesados {len(df_palmolive)} productos Palmolive")
    else:
        print(f"⚠ No se encontró {palmolive_path}")
    
    # Crear estructura final
    prices_data = {
        'metadata': {
            'total_productos': len(productos_con_precios),
            'productos_colgate': sum(1 for p in productos_con_precios if p['marca'] == 'Colgate'),
            'productos_palmolive': sum(1 for p in productos_con_precios if p['marca'] == 'Palmolive'),
            'generado': '2025-11-07'
        },
        'productos': productos_con_precios
    }
    
    # Guardar JSON
    output_path = qa_dir / 'prices.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(prices_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Archivo de precios generado exitosamente en {output_path}")
    print(f"📊 Total de productos con precios: {len(productos_con_precios)}")
    print(f"   - Colgate: {prices_data['metadata']['productos_colgate']}")
    print(f"   - Palmolive: {prices_data['metadata']['productos_palmolive']}")


if __name__ == "__main__":
    main()
