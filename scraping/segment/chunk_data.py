
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Dict, List


def chunk_text(text: str, max_words: int = 150, overlap_words: int = 30) -> List[str]:

    if not text:
        return []
    if max_words <= 0:
        raise ValueError("max_words debe ser un entero positivo")

    if overlap_words < 0 or overlap_words >= max_words:
        overlap_words = 0
    words = text.split()
    chunks: List[str] = []
    index = 0
    total_words = len(words)
    while index < total_words:
        end = min(index + max_words, total_words)
        chunk_words = words[index:end]
        chunks.append(" ".join(chunk_words))
        if end == total_words:
            break
        index += max_words - overlap_words
    return chunks


def chunk_data(
    input_file: Path,
    output_file: Path,
    max_words: int = 200,
    overlap_words: int = 30,
) -> None:

    with input_file.open("r", encoding="utf-8") as f:
        cleaned_data: List[Dict[str, str]] = json.load(f)

    chunked_data: List[Dict[str, str]] = []
    for entry in cleaned_data:
        url = entry.get("url", "")
        text = entry.get("text") or ""
        title = entry.get("titulo", "")
        date = entry.get("fecha_scraping", "")
        fragments = chunk_text(text, max_words=max_words, overlap_words=overlap_words)
        # Determinar un slug para el chunk_id basado en la URL
        slug = url.rstrip("/").split("/")[-1] or "root"
        for i, frag in enumerate(fragments):
            chunk_id = f"{slug}_{i}"
            chunked_data.append(
                {
                    "url": url,
                    "titulo": title,
                    "fecha_scraping": date,
                    "chunk_id": chunk_id,
                    "text": frag,
                }
            )

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(chunked_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    default_input = Path("../limp/colgate_data_clean.json")
    default_output = Path("colgate_chunks.json")
    default_max_words = 150
    default_overlap = 30
    input_path = default_input
    output_path = default_output
    max_words = default_max_words
    overlap_words = default_overlap

    chunk_data(input_path, output_path, max_words=max_words, overlap_words=overlap_words)
    print(
        f"Fragmentos generados guardados en {output_path}. "
        f"Tamaño de chunk={max_words}, solapamiento={overlap_words}."
    )