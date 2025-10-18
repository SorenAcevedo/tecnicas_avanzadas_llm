"""
Módulo de preprocesamiento para productos Colgate y Palmolive.

Este módulo proporciona funciones para limpiar, normalizar y estructurar los datos de productos
de diferentes orígenes (Colgate y Palmolive), dejándolos listos para chunking y generación de embeddings.
Incluye funciones para limpiar textos, parsear campos tipo lista y aplicar el preprocesamiento
a DataFrames de pandas.
"""

import re
import json

import pandas as pd


def clean_text(text: str) -> str:
    """
    Limpia y normaliza un texto eliminando saltos de línea, espacios dobles y caracteres extraños.

    Args:
        text (str): Texto a limpiar.

    Returns:
        str: Texto limpio y normalizado.
    """

    text = str(text)
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = text.replace("\xa0", " ")
    return text.strip()


def parse_list_field(field: str) -> list:
    """
    Convierte un string JSON de lista en lista de Python, o retorna lista vacía si hay error.

    Args:
        field (str): String que representa una lista en formato JSON.

    Returns:
        list: Lista de Python resultante o lista vacía.
    """
    try:
        return json.loads(field) if field and field != "[]" else []
    except Exception:
        return []


def preprocess_row(row: pd.Series, schema: str) -> pd.Series:
    """
    Preprocesa una fila de producto según el esquema (colgate o palmolive).
    Limpia textos, parsea campos complejos y rellena campos faltantes.

    Args:
        row (pd.Series): Fila del DataFrame de productos.
        schema (str): 'colgate' o 'palmolive'.

    Returns:
        pd.Series: Fila preprocesada y normalizada.
    """
    # Campos comunes
    row["nombre"] = clean_text(row.get("nombre", ""))
    row["descripcion_larga"] = clean_text(row.get("descripcion_larga", ""))
    row["beneficios"] = parse_list_field(row.get("beneficios", ""))
    row["sku"] = clean_text(row.get("sku", ""))
    row["url_detalle"] = clean_text(row.get("url_detalle", ""))
    row["imagen"] = clean_text(row.get("imagen", ""))
    row["tiendas"] = parse_list_field(row.get("tiendas", ""))

    # Específicos de Colgate
    if schema == "colgate":
        row["descripcion"] = clean_text(row.get("descripcion", ""))
        row["categoria"] = clean_text(row.get("categoria", ""))
        row["marca"] = clean_text(row.get("marca", ""))
        row["faqs"] = parse_list_field(row.get("faqs", ""))
        # Palmolive no tiene estos campos, así que los rellena vacíos si no existen
        for field in ["tags", "titulo", "ingredientes", "fragancia", "modo_uso"]:
            row[field] = clean_text(row.get(field, ""))

    # Específicos de Palmolive
    if schema == "palmolive":
        row["tags"] = parse_list_field(row.get("tags", ""))
        row["titulo"] = clean_text(row.get("titulo", ""))
        row["ingredientes"] = clean_text(row.get("ingredientes", ""))
        row["fragancia"] = clean_text(row.get("fragancia", ""))
        row["modo_uso"] = clean_text(row.get("modo_uso", ""))
        # Colgate no tiene estos campos, así que los rellena vacíos si no existen
        for field in ["descripcion", "categoria", "marca", "faqs"]:
            if field == "faqs":
                row[field] = []
            else:
                row[field] = clean_text(row.get(field, ""))

    return row


def preprocess_csv(
    input_path: str, schema: str, output_path: str = None
) -> pd.DataFrame:
    """
    Preprocesa un CSV de productos Colgate o Palmolive y lo guarda como pickle o CSV limpio.

    Args:
        input_path (str): Ruta al archivo CSV de entrada.
        schema (str): 'colgate' o 'palmolive'.
        output_path (str, opcional): Ruta de salida para guardar el DataFrame preprocesado.

    Returns:
        pd.DataFrame: DataFrame preprocesado.
    """
    df = pd.read_csv(input_path)
    df = df.apply(lambda row: preprocess_row(row, schema), axis=1)
    if output_path:
        if output_path.endswith(".pkl"):
            df.to_pickle(output_path)
        else:
            df.to_csv(output_path, index=False, encoding="utf-8-sig")
    return df


if __name__ == "__main__":
    df_colgate = preprocess_csv(
        "./data/raw/productos_colgate.csv",
        schema="colgate",
        output_path="./data/processed/productos_colgate_clean.csv",
    )
    df_palmolive = preprocess_csv(
        "./data/raw/productos_palmolive.csv",
        schema="palmolive",
        output_path="./data/processed/productos_palmolive_clean.csv",
    )
    print("Preprocesamiento completado.")
