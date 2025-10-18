"""
Módulo de chunking para productos Colgate y Palmolive.

Este módulo toma un DataFrame preprocesado y genera chunks semánticos por campo relevante,
listos para embeddings y retrieval. Cada chunk mantiene la referencia al producto (sku, nombre, etc.).
"""

import spacy
import pandas as pd

import argparse
import json

nlp = spacy.blank("es")


def chunk_text(text, chunk_size=256, overlap=50):
    """
    Divide un texto largo en chunks de tamaño fijo (por tokens) con solapamiento.
    Args:
        text (str): Texto a dividir.
        chunk_size (int): Tamaño de chunk en tokens.
        overlap (int): Número de tokens de solapamiento entre chunks.
    Returns:
        list[str]: Lista de chunks de texto.
    """
    tokens = [t.text for t in nlp(str(text))]
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk = " ".join(tokens[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def chunk_product_row(row, chunk_size=256, overlap=50):
    """
    Genera chunks semánticos para un producto (una fila del DataFrame).
    Args:
        row (pd.Series): Fila de producto preprocesada.
        chunk_size (int): Tamaño de chunk para textos largos.
        overlap (int): Solapamiento de tokens.
    Returns:
        list[dict]: Lista de dicts con los chunks y metadatos.
    """
    chunks = []
    sku = row.get("sku", "")
    nombre = row.get("nombre", "")
    # Chunk de descripción larga
    if row.get("descripcion_larga"):
        for chunk in chunk_text(row["descripcion_larga"], chunk_size, overlap):
            chunks.append(
                {
                    "sku": sku,
                    "nombre": nombre,
                    "tipo_chunk": "descripcion_larga",
                    "contenido": chunk,
                }
            )
    # Chunk de beneficios (uno por beneficio)
    for beneficio in row.get("beneficios", []):
        if beneficio:
            chunks.append(
                {
                    "sku": sku,
                    "nombre": nombre,
                    "tipo_chunk": "beneficio",
                    "contenido": beneficio,
                }
            )
    # Chunk de FAQs (uno por pregunta-respuesta)
    for faq in row.get("faqs", []):
        if isinstance(faq, dict):
            contenido = f"{faq.get('pregunta','')} {faq.get('respuesta','')}"
        else:
            contenido = str(faq)
        if contenido.strip():
            chunks.append(
                {
                    "sku": sku,
                    "nombre": nombre,
                    "tipo_chunk": "faq",
                    "contenido": contenido,
                }
            )
    # Chunk de tiendas (uno por tienda)
    for tienda in row.get("tiendas", []):
        if isinstance(tienda, dict):
            contenido = f"{tienda.get('tienda','')}, {tienda.get('disponibilidad','')}, {tienda.get('precio','')}"
        else:
            contenido = str(tienda)
        if contenido.strip():
            chunks.append(
                {
                    "sku": sku,
                    "nombre": nombre,
                    "tipo_chunk": "tienda",
                    "contenido": contenido,
                }
            )
    # Palmolive: ingredientes, fragancia, modo_uso, tags
    for campo in ["ingredientes", "fragancia", "modo_uso", "tags"]:
        valor = row.get(campo, None)
        if isinstance(valor, list):
            for v in valor:
                if v:
                    chunks.append(
                        {
                            "sku": sku,
                            "nombre": nombre,
                            "tipo_chunk": campo,
                            "contenido": v,
                        }
                    )
        elif valor and isinstance(valor, str) and valor.strip():
            chunks.append(
                {"sku": sku, "nombre": nombre, "tipo_chunk": campo, "contenido": valor}
            )
    return chunks


def chunk_dataframe(df, chunk_size=256, overlap=50):
    """
    Genera todos los chunks para un DataFrame de productos.
    Args:
        df (pd.DataFrame): DataFrame preprocesado.
        chunk_size (int): Tamaño de chunk para textos largos.
        overlap (int): Solapamiento de tokens.
    Returns:
        list[dict]: Lista de todos los chunks generados.
    """
    all_chunks = []
    for _, row in df.iterrows():
        all_chunks.extend(chunk_product_row(row, chunk_size, overlap))
    return all_chunks


if __name__ == "__main__":
    # Chunk Colgate
    df_colgate = pd.read_csv("./data/processed/productos_colgate_clean.csv")
    chunks_colgate = chunk_dataframe(df_colgate, chunk_size=256, overlap=50)
    pd.DataFrame(chunks_colgate).to_csv("./data/processed/chunks_colgate.csv", index=False, encoding="utf-8-sig")

    # Chunk Palmolive
    df_palmolive = pd.read_csv("./data/processed/productos_palmolive_clean.csv")
    chunks_palmolive = chunk_dataframe(df_palmolive, chunk_size=256, overlap=50)
    pd.DataFrame(chunks_palmolive).to_csv("./data/processed/chunks_palmolive.csv", index=False, encoding="utf-8-sig")

    print("Chunking completado para Colgate y Palmolive.")
