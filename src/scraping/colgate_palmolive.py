import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import json

START_URL = "https://www.colgatepalmolive.com.co/"
MAX_PAGES = 100  # Set a reasonable limit to avoid infinite crawling
CRAWL_DELAY = 1  # seconds between requests

visited = set()
queue = [START_URL]
all_urls = set()

while queue and len(visited) < MAX_PAGES:
    url = queue.pop(0)
    if url in visited:
        continue
    print(f"Crawling: {url}")
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            continue
        soup = BeautifulSoup(resp.text, "html.parser")
        visited.add(url)
        all_urls.add(url)
        # Find all internal links
        for a in soup.find_all("a", href=True):
            link = a["href"]
            # Normalize link
            abs_link = urljoin(url, link)
            # Skip anchor links (fragments)
            parsed = urlparse(abs_link)
            abs_link_no_fragment = parsed._replace(fragment="").geturl()
            # Only crawl links within the same domain and without fragment
            if parsed.netloc == urlparse(START_URL).netloc:
                if abs_link_no_fragment not in visited and abs_link_no_fragment not in queue:
                    queue.append(abs_link_no_fragment)
        time.sleep(CRAWL_DELAY)
    except Exception as e:
        print(f"Error crawling {url}: {e}")

# Save results
import os
os.makedirs("scraping/extrac", exist_ok=True)
with open("scraping/extrac/colgate_urls_crawled.json", "w", encoding="utf-8") as f:
    json.dump(sorted(list(all_urls)), f, ensure_ascii=False, indent=2)

print(f"Crawled {len(all_urls)} URLs. Saved to scraping/extrac/colgate_urls_crawled.json.")


import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json
import os
from datetime import datetime

# PDF extraction
try:
    import pdfplumber
except ImportError:
    pdfplumber = None
    print("pdfplumber not installed. PDF extraction will be skipped.")

URLS_FILE = "scraping/extrac/urls_selected.json"
OUTPUT_FILE = "scraping/extrac/colgate_data.json"

def fetch_html(url):
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            return None, None
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.title.string.strip() if soup.title else urlparse(url).path.split("/")[-1]
        text = soup.get_text(separator="\n", strip=True)
        return title, text
    except Exception as e:
        print(f"Error fetching HTML {url}: {e}")
        return None, None

def fetch_pdf(url):
    if not pdfplumber:
        return None, None
    try:
        resp = requests.get(url, timeout=20)
        if resp.status_code != 200:
            return None, None
        # Save PDF temporarily
        tmp_pdf = "_tmp_colgate.pdf"
        with open(tmp_pdf, "wb") as f:
            f.write(resp.content)
        text = ""
        with pdfplumber.open(tmp_pdf) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
                text += "\n"
        os.remove(tmp_pdf)
        title = url.split("/")[-1]
        return title, text.strip()
    except Exception as e:
        print(f"Error fetching PDF {url}: {e}")
        return None, None

def main():
    with open(URLS_FILE, "r", encoding="utf-8") as f:
        urls = json.load(f)
    # Filter for palmolive and colgate only
    filtered_urls = [
        url for url in urls
        if ("palmolive" in url.lower() or "colgate" in url.lower())
    ]
    print(f"Processing {len(filtered_urls)} filtered URLs (palmolive/colgate only)")
    results = []
    today = datetime.now().strftime("%Y-%m-%d")
    for url in filtered_urls:
        print(f"Processing: {url}")
        if url.lower().endswith(".pdf"):
            title, text = fetch_pdf(url)
            ctype = "pdf"
        else:
            title, text = fetch_html(url)
            ctype = "html"
        if not text:
            print(f"No content for {url}")
            continue
        results.append({
            "url": url,
            "titulo": title or url,
            "fecha_scraping": today,
            "type": ctype,
            "text": text
        })
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(results)} entries to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

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