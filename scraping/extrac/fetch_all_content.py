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
