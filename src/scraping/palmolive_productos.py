"""
Módulo para scrapear productos de Palmolive y sus categorías
"""

from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def extraer_tabs_producto(soup):
    """
    Extrae el contenido de las pestañas 'Ingredientes', 'Fragancia' y 'Modo de uso'
    sin depender de los IDs dinámicos.
    Retorna un diccionario con los textos limpios.
    """
    data = {"ingredientes": None, "fragancia": None, "modo_uso": None}

    # Buscar todos los divs con clase 'tabs-content'
    for tab in soup.select("div.tabs-content"):
        # Dentro de cada tab, buscar el título h2
        h2 = tab.select_one("div.richText-content h2")
        p = tab.select_one("div.richText-content p")

        if not h2 or not p:
            continue

        titulo = h2.get_text(strip=True).lower()
        contenido = p.get_text(strip=True)

        if "ingrediente" in titulo:
            data["ingredientes"] = contenido
        elif "fragancia" in titulo:
            data["fragancia"] = contenido
        elif "modo" in titulo or "uso" in titulo:
            data["modo_uso"] = contenido

    return data


def scrape_product_detail(product_url):
    """Extrae fragancia, modo de uso e ingredientes desde la página del producto."""
    resp = requests.get(product_url)
    soup = BeautifulSoup(resp.text, "html.parser")

    details = {"ingredientes": None, "fragancia": None, "modo_uso": None}

    # Buscar todas las pestañas (tabs)
    tabs = soup.select("ul.tabs-nav-list a")

    for tab in tabs:
        tab_name = tab.get_text(strip=True).lower()
        href = tab.get("href")

        if not href or not href.startswith("#"):
            continue

        tab_id = href.lstrip("#")
        content_div = soup.find(id=tab_id)

        if not content_div:
            continue

        content_text = content_div.get_text(" ", strip=True)

        if "ingrediente" in tab_name:
            details["ingredientes"] = content_text
        elif "fragancia" in tab_name:
            details["fragancia"] = content_text
        elif "uso" in tab_name:
            details["modo_uso"] = content_text

    return details


def obtener_tiendas(driver):
    """
    Hace clic en el botón 'Comprar ahora', espera a que aparezca el modal
    y extrae las tiendas con su disponibilidad y precio.
    """
    try:
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

        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div.csWidgetRetailerRow")
            )
        )
        time.sleep(1)

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


# Configuración del driver
service = Service(executable_path="./driver/chromedriver.exe")
driver = webdriver.Chrome(service=service)

# 1. Página principal
url = "https://www.palmolive.co/productos"
driver.get(url)
time.sleep(5)

products = []
soup = BeautifulSoup(driver.page_source, "html.parser")

# En Palmolive, cada producto está dentro de un <li class="articleList-article">
cards = soup.select("li.articleList-article")
print(f"Encontradas {len(cards)} cards en esta página.")

for card in cards:
    nombre_tag = card.select_one("h3.articleList-title a")
    desc_tag = card.select_one("div.articleList-description-content")
    img_tag = card.select_one("img.articleList-thumbnail")
    link_tag = card.select_one("h3.articleList-title a")
    tags = [li.get_text(strip=True) for li in card.select("ul.articleList-tags li")]

    nombre = nombre_tag.get_text(strip=True) if nombre_tag else ""
    descripcion = desc_tag.get_text(" ", strip=True) if desc_tag else ""
    imagen = img_tag.get("src") if img_tag else ""
    url_detalle = (
        "https://www.palmolive.co" + link_tag["href"]
        if link_tag and link_tag["href"].startswith("/")
        else link_tag["href"] if link_tag else ""
    )

    products.append(
        {
            "nombre": nombre,
            "descripcion": descripcion,
            "imagen": imagen,
            "url_detalle": url_detalle,
            "tags": tags,
        }
    )

# 2. Recorremos los detalles (idéntico al script previo)
for product in products:
    try:
        if not product["url_detalle"]:
            continue

        driver.get(product["url_detalle"])
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # --- 1️⃣ Título completo ---
        h1_tag = soup.select_one("div.product-main-description h1")
        titulo = (
            h1_tag.get_text(" ", strip=True).replace("\xa0", " ")
            if h1_tag
            else product["nombre"]
        )

        # --- 2️⃣ Descripción larga (primer párrafo grande) ---
        desc_block = soup.select_one(
            "div.richText.component.section.no-margin-paragraphs"
        )
        descripcion_larga = (
            desc_block.get_text(" ", strip=True).replace("\xa0", " ")
            if desc_block
            else ""
        )

        # --- 3️⃣ Beneficios (después de <h2> Beneficios) ---
        beneficios = []
        beneficios_section = soup.find("h2", string=lambda s: s and "Beneficios" in s)
        if beneficios_section:
            # tomamos los <p> que siguen hasta el próximo h2 o fin
            for p in beneficios_section.find_all_next("p"):
                text = p.get_text(strip=True)
                if not text or "Ingrediente" in text:
                    break
                beneficios.append(text)


        # Fragancia

        # --- 6️⃣ SKU del botón "Comprar" ---
        boton = soup.select_one("button.button-buy-now-channel-sight")
        sku = (
            boton["data-product-sku"]
            if boton and boton.has_attr("data-product-sku")
            else ""
        )

        # --- 7️⃣ Tiendas (igual que antes, modal ChannelSight) ---
        tiendas = obtener_tiendas(driver)
        
        products_tabs = extraer_tabs_producto(soup)
        ingredientes = products_tabs["ingredientes"]
        fragancia = products_tabs["fragancia"]
        modo_uso = products_tabs["modo_uso"]

        # --- 8️⃣ Guardar todo ---
        product["titulo"] = titulo
        product["descripcion_larga"] = descripcion_larga
        product["beneficios"] = beneficios
        product["ingredientes"] = ingredientes
        
        product["fragancia"] = fragancia
        product["modo_uso"] = modo_uso
        product["sku"] = sku
        product["tiendas"] = tiendas

    except Exception as e:
        print(f"⚠️ Error en {product['nombre']}: {e}")
        continue

driver.quit()

# 3. Guardar CSV
df = pd.DataFrame(products)
df.to_csv("../../data/raw/productos_palmolive.csv", index=False, encoding="utf-8-sig")

print("\n✅ Scraping completado y CSV guardado correctamente.")
