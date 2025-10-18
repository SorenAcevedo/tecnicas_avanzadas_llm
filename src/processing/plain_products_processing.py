"""
Script para convertir los CSV de productos Colgate y Palmolive en archivos TXT de contexto para el asistente.
Cada producto se serializa como un bloque de texto legible, uno por línea.
"""

import pandas as pd
import os

def colgate_row_to_text(row):
    return (
        f"Nombre: {row['nombre']}\n"
        f"Descripción: {row['descripcion']}\n"
        f"Imagen: {row['imagen']}\n"
        f"URL Detalle: {row['url_detalle']}\n"
        f"SKU: {row['sku']}\n"
        f"Categoría: {row['categoria']}\n"
        f"Marca: {row['marca']}\n"
        f"Beneficios: {row['beneficios']}\n"
        f"Descripción larga: {row['descripcion_larga']}\n"
        f"FAQs: {row['faqs']}\n"
        f"Tiendas: {row['tiendas']}\n"
        "---"
    )

def palmolive_row_to_text(row):
    return (
        f"Nombre: {row['nombre']}\n"
        f"Imagen: {row['imagen']}\n"
        f"URL Detalle: {row['url_detalle']}\n"
        f"Tags: {row['tags']}\n"
        f"Título: {row['titulo']}\n"
        f"Descripción larga: {row['descripcion_larga']}\n"
        f"Beneficios: {row['beneficios']}\n"
        f"Ingredientes: {row['ingredientes']}\n"
        f"Fragancia: {row['fragancia']}\n"
        f"Modo de uso: {row['modo_uso']}\n"
        f"SKU: {row['sku']}\n"
        f"Tiendas: {row['tiendas']}\n"
        "---"
    )

def csv_to_txt(input_csv, output_txt, row_to_text):
    df = pd.read_csv(input_csv)
    with open(output_txt, 'w', encoding='utf-8') as f:
        for _, row in df.iterrows():
            f.write(row_to_text(row))
            f.write('\n')

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    processed_dir = os.path.join(base_dir, 'data', 'processed')
    raw_dir = os.path.join(base_dir, 'data', 'raw')
    csv_to_txt(
        os.path.join(raw_dir, 'productos_colgate.csv'),
        os.path.join(processed_dir, 'context_colgate.txt'),
        colgate_row_to_text
    )
    csv_to_txt(
        os.path.join(raw_dir, 'productos_palmolive.csv'),
        os.path.join(processed_dir, 'context_palmolive.txt'),
        palmolive_row_to_text
    )
    print("Archivos de contexto generados correctamente.")

if __name__ == "__main__":
    main()
