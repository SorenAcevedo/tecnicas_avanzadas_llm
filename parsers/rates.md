# Banco de Occidente — Selectores iniciales (Tasas / rates)

## Fuente
- URL: (pega aquí la URL exacta donde el banco publica las **tasas**)
- Nota: si no hay tabla HTML y usan **PDF**, capturar el enlace al PDF igualmente.

## Estructura esperada (CSS para Scrapy)
- **Tabla principal**: `table, .table, .rates-table`
- **Filas**: `tbody tr`
- **Encabezados esperados** (mapeo → schema):
  - "Producto" → `product_name`
  - "Tasa Efectiva Anual" / "EA" → `value`
  - "Vigencia" / "Desde" → `effective_from`

## Mapeo → schema `rates`
- `product_name` ← texto de la celda "Producto"
- `rate_type`    ← `"EA"` (si el encabezado dice EA; si hay NMV, capturar `"NMV"`)
- `value`        ← número; limpiar `%`, puntos y comas (`"12,50%” → 12.5`)
- `effective_from` ← fecha normalizada a `YYYY-MM-DD` (si viene dd/mm/yyyy, convertir)
- `source_url`   ← `response.url`
- `extracted_at` ← timestamp de extracción

## Fallbacks
- Si no hay tabla HTML:
  - Buscar enlaces a PDF: `a[href$=".pdf"], a:contains("PDF"), a:contains("tasas"), a:contains("tarifas")`
  - Guardar `url_pdf` y procesar el PDF en una etapa aparte.
- Si hay múltiples tablas, elegir la que tenga encabezados que contengan “Tasa” y “Producto”.

## Ejemplo mínimo (referencia)
```python
rows = response.css("table, .table, .rates-table").css("tbody tr")
for r in rows:
    cols = [c.get().strip() for c in r.css("td *::text, td::text").getall() if c.strip()]
    # ajusta índices según el orden real de columnas
    product = r.css("td:nth-child(1) *::text, td:nth-child(1)::text").get(default="").strip()
    rate_txt = r.css("td:nth-child(2) *::text, td:nth-child(2)::text").get(default="").strip()
    vig_txt  = r.css("td:nth-child(3) *::text, td:nth-child(3)::text").get(default="").strip()

    # normalización rápida
    rate_num = rate_txt.replace("%","").replace(".","").replace(",",".")
    try:
        rate_val = float(rate_num)
    except:
        rate_val = None

    yield {
        "product_name": product,
        "rate_type": "EA",  # ajustar si detectas NMV u otra
        "value": rate_val,
        "effective_from": vig_txt,  # normalizar a YYYY-MM-DD en pipeline
        "source_url": response.url,
    }

# Fallback PDF
for a in response.css('a[href$=".pdf"], a:contains("PDF"), a:contains("tasas"), a:contains("tarifas")'):
    yield {"url_pdf": response.urljoin(a.attrib.get("href","")), "source_url": response.url}

