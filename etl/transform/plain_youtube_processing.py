"""
Script para convertir los videos de YouTube (JSON) en un archivo TXT de contexto para el asistente.
Solo incluye videos publicados en 2024 o después, con título, descripción y url.
"""

import json
import os
from datetime import datetime

def video_to_text(video):
    return (
        f"Título: {video.get('title', '').strip()}\n"
        f"Descripción: {video.get('description', '').strip()}\n"
        f"URL: {video.get('url', '').strip()}\n"
        "---"
    )

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    raw_dir = os.path.join(base_dir, 'data', 'raw')
    processed_dir = os.path.join(base_dir, 'data', 'processed')
    input_json = os.path.join(raw_dir, 'youtube_channel_videos.json')
    output_txt = os.path.join(processed_dir, 'context_youtube.txt')

    with open(input_json, 'r', encoding='utf-8') as f:
        videos = json.load(f)

    with open(output_txt, 'w', encoding='utf-8') as f:
        for video in videos:
            published = video.get('publishedAt')
            if not published:
                continue
            try:
                year = int(published[:4])
            except Exception:
                continue
            if year >= 2024:
                f.write(video_to_text(video))
                f.write('\n')
    print("Archivo de contexto de videos generado correctamente.")

if __name__ == "__main__":
    main()
