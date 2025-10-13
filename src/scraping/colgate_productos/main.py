"""
Módulo para scrapear productos de Colgate y sus categorías
"""

from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json
import time


def obtener_tiendas(driver):
    """
    Hace clic en el botón 'Comprar ahora', espera a que aparezca el modal
    y extrae las tiendas con su disponibilidad y precio.

    Parámetros:
      driver: instancia de selenium webdriver con la página del producto ya cargada.

    Retorna:
      list[dict]: lista de {"tienda": str, "disponibilidad": str, "precio": str}
    """
    try:
        # Esperar y hacer clic en el botón 'Comprar ahora'
        boton = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "button.swn-tag-wtb-btn, button[ps-sku], button[data-product-sku]",
                )
            )
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", boton)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", boton)

        # Esperar a que aparezcan las filas del modal
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div.csWidgetRetailerRow")
            )
        )
        time.sleep(1)  # breve pausa para asegurar carga completa

        # Parsear el contenido del modal
        soup = BeautifulSoup(driver.page_source, "html.parser")
        rows = soup.select("div.csWidgetRetailerRow")

        tiendas = []
        for row in rows:
            tienda = row.select_one(".csWidgetRetailerImg")
            disponibilidad = row.select_one(".csWidgetProductStock div")
            precio = row.select_one(".csWidgetPrice")

            tiendas.append(
                {
                    "tienda": tienda.get("alt", "").strip() if tienda else "",
                    "disponibilidad": (
                        disponibilidad.get_text(" ", strip=True)
                        if disponibilidad
                        else ""
                    ),
                    "precio": precio.get_text(" ", strip=True) if precio else "",
                }
            )

        return tiendas

    except Exception:
        return []


service = Service(executable_path="../driver/chromedriver.exe")
driver = webdriver.Chrome(service=service)

# 1. Página principal
url = "https://www.colgate.com/es-co/products"
driver.get(url)
time.sleep(5)

products = []
soup = BeautifulSoup(driver.page_source, "html.parser")

cards = soup.select("div.grid-item-product")
print(f"Encontradas {len(cards)} cards en esta página.")

for card in cards:
    nombre = card.select_one("h3.product-title")
    desc = card.select_one("div.product-description p")
    img = card.select_one("img.product-image-asset")
    link = card.select_one("a.product-detail-link")
    sku_btn = card.select_one("button[data-product-sku]")

    products.append(
        {
            "nombre": nombre.get_text(strip=True) if nombre else "",
            "descripcion": desc.get_text(" ", strip=True) if desc else "",
            "imagen": img.get("src") or img.get("data-src") if img else "",
            "url_detalle": link["href"] if link else "",
            "sku": sku_btn["data-product-sku"] if sku_btn else "",
        }
    )

# 2. Recorremos los detalles
for product in products:
    try:
        driver.get(product["url_detalle"])
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Categoría → último breadcrumb
        breadcrumb_items = soup.select("nav.cmp-breadcrumb span[itemprop='name']")
        categoria = (
            breadcrumb_items[-1].get_text(strip=True)
            if len(breadcrumb_items) > 2
            else ""
        )

        # Marca → h2.product-detail-subtitle
        marca_tag = soup.select_one("h2.product-detail-subtitle a")
        marca = marca_tag.get_text(strip=True) if marca_tag else ""

        # Beneficios → div.field-text
        beneficios = [b.get_text(strip=True) for b in soup.select("div.field-text")]

        # Descripción general → div.banner-description
        desc_larga = soup.select_one("div.banner-description")
        descripcion_larga = desc_larga.get_text(" ", strip=True) if desc_larga else ""

        # Preguntas frecuentes → pares de segmentos bold/none
        faqs = []

        # Cada bloque de FAQ está dentro de un div.text-segments que contiene una pregunta (.segment.bold)
        faq_blocks = soup.select("div.text-segments")

        for block in faq_blocks:
            # Solo tomamos los bloques que contengan al menos una pregunta y una respuesta
            preguntas = block.select(".segment.bold")
            respuestas = block.select(".segment.none")

            # Si no hay ambos, se salta (así evitamos los del nav-bar)
            if not preguntas or not respuestas:
                continue

            # Ahora iteramos emparejando solo los que están dentro del mismo bloque
            for q, a in zip(preguntas, respuestas):
                faqs.append(
                    {
                        "pregunta": q.get_text(strip=True),
                        "respuesta": a.get_text(" ", strip=True),
                    }
                )

        # Agregar los nuevos campos
        product["categoria"] = categoria
        product["marca"] = marca
        product["beneficios"] = beneficios
        product["descripcion_larga"] = descripcion_larga
        product["faqs"] = faqs
        product["tiendas"] = obtener_tiendas(driver)

        print(f"{product['nombre']} — {categoria}")

    except Exception as e:
        print(f"Error en {product['nombre']}: {e}")
        continue

driver.quit()

# 3. Guardar en CSV
df = pd.DataFrame(products)
df.to_csv("../../../data/raw/productos_colgate.csv", index=False, encoding="utf-8-sig")

print("\n✅ Scraping completado y CSV guardado correctamente.")
