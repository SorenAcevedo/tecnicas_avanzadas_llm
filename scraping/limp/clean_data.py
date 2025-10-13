from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Dict, List


# Palabras clave a eliminar del texto (en minúsculas).  El usuario ha solicitado
# filtrar únicamente estas dos palabras, pero puedes añadir más términos según
# las páginas que vayas scrapeando.
ex_words: List[str] = [
    "cookie",
    "search",
]

# Patrón para detectar URLs en una línea.
urls_clean = re.compile(r"https?://\S+")


def clean_text(text: str) -> str:

    if not text:
        return ""
    cleaned_lines: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # Elimina alt text de imágenes
        if stripped.lower().startswith("image:"):
            continue
        # Elimina encabezados vacíos (##, ###, etc.)
        if re.fullmatch(r"#+", stripped):
            continue
        # Filtra palabras clave
        lower_line = stripped.lower()
        if any(keyword in lower_line for keyword in ex_words):
            continue
        # Elimina URLs sueltas
        if urls_clean.fullmatch(stripped):
            continue
        cleaned_lines.append(stripped)
    return "\n".join(cleaned_lines)


def clean_data(input_file: Path, output_file: Path) -> None:

    with input_file.open("r", encoding="utf-8") as f:
        raw_data: List[Dict[str, str]] = json.load(f)

    cleaned_data: List[Dict[str, str]] = []
    for entry in raw_data:
        url = entry.get("url", "")
        raw_text = entry.get("text") or ""
        title = entry.get("titulo", "")
        date = entry.get("fecha_scraping", "")
        cleaned = clean_text(raw_text)
        cleaned_data.append(
            {
                "url": url,
                "titulo": title,
                "fecha_scraping": date,
                "text": cleaned,
            }
        )

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # Valores por defecto
    default_input = Path("../extrac/colgate_data.json")
    default_output = Path("colgate_data_clean.json")
    args = sys.argv[1:]
    input_path = Path(args[0]) if len(args) >= 1 else default_input
    output_path = Path(args[1]) if len(args) >= 2 else default_output
    clean_data(input_path, output_path)
    print(f"Datos limpiados guardados en {output_path}")