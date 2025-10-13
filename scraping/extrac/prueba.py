from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup  # type: ignore
from selenium import webdriver  # type: ignore
from selenium.webdriver.chrome.service import Service  # type: ignore
from webdriver_manager.chrome import ChromeDriverManager  # type: ignore


def scrape_page(url: str, driver: webdriver.Chrome, wait_seconds: int = 5) -> dict[str, str | None]:
    """Extrae texto visible y metadatos de una URL usando Selenium."""
    try:
        driver.get(url)
        time.sleep(wait_seconds)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # Extraer título si existe
        title = soup.title.string.strip() if soup.title else "Sin título"

        # Extraer texto visible
        text = soup.get_text(separator="\n", strip=True)

        return {
            "url": url,
            "titulo": title,
            "fecha_scraping": datetime.now().strftime("%Y-%m-%d"),
            "text": text
        }
    except Exception as e:
        print(f"Error al procesar {url}: {e}")
        return {
            "url": url,
            "titulo": None,
            "fecha_scraping": datetime.now().strftime("%Y-%m-%d"),
            "text": None
        }


def scrape_urls(urls: list[str], wait_seconds: int = 5) -> list[dict[str, str | None]]:
    """Recorre una lista de URLs y extrae texto y metadatos."""
    results: list[dict[str, str | None]] = []
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        for url in urls:
            print(f"Visitando {url}...")
            result = scrape_page(url, driver, wait_seconds)
            results.append(result)
    finally:
        driver.quit()

    return results


def save_results(data: list[dict[str, str | None]], output_file: str = "colgate_data.json") -> None:
    """Guarda los resultados en un archivo JSON."""
    path = Path(output_file)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    urls = [
        "https://www.colgatepalmolive.com/en-us/who-we-are/history",
        "https://www.colgatepalmolive.com.co/",
        "https://www.colgatepalmolive.com.co/contact-us",
        # Agrega más URLs aquí
    ]

    results = scrape_urls(urls)
    output_name = Path("scraping/extrac/colgate_data.json")
    save_results(results, output_name)
    print(f"Scraping completado. Se han guardado {len(results)} página(s) en {output_name}.")
