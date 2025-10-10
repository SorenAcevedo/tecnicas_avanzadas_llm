# Banco de Occidente — Selectores iniciales (Tarifas / fees)

## Fuente
- URL (landing): https://portalpublico.bancodeoccidente.com.co/tarifas
PDF Personas:  https://portalpublico.bancodeoccidente.com.co/documents/d/guest/tarifas-persona-2-
PDF Empresas:  https://portalpublico.bancodeoccidente.com.co/documents/d/guest/tarifas-empresariales-1-

- Si no hay tabla HTML y usan **PDF**, capturar el enlace al PDF.

## Estructura esperada (CSS para Scrapy)
- **Tabla principal**: `table, .table, .fees-table`
- **Filas**: `tbody tr`
- **Encabezados esperados** (mapeo → schema):
  - "Producto" → `product_ref` (o `product_name` si aún no hay ID)
  - "Concepto" → `concept`
  - "Valor" / "$" → `amount` (+ `currency="COP"`)
  - "Periodicidad" → `periodicity`
  - "Vigencia" / "Desde" → `effective_from`

## Mapeo → schema `fees`
- `product_ref`  ← texto de la celda "Producto"
- `concept`      ← texto de la celda "Concepto"
- `amount`       ← número; limpiar `$`, puntos y comas (`"23.000"` → `23000`)
- `currency`     ← `"COP"`
- `periodicity`  ← normalizar: mensual → `monthly`, por transacción → `per_transaction`
- `effective_from` ← fecha a `YYYY-MM-DD` (normalizar en pipeline)
- `source_url`   ← `response.url`
- `extracted_at` ← timestamp

## Fallbacks
- Si no hay tabla HTML:
  - Buscar PDFs: `a[href$=".pdf"], a:contains("PDF"), a:contains("tarifas"), a:contains("comisiones")`
  - Emite `{"url_pdf": absolute_url, "source_url": response.url}` para parsing posterior.
- Si hay varias tablas, seleccionar la que contenga encabezados con “Concepto” y “Valor”.

## Ejemplo mínimo (referencia)
```python
rows = response.css("table, .table, .fees-table").css("tbody tr")
for r in rows:
    producto = r.css("td:nth-child(1) *::text, td:nth-child(1)::text").get(default="").strip()
    concepto = r.css("td:nth-child(2) *::text, td:nth-child(2)::text").get(default="").strip()
    valor_txt = r.css("td:nth-child(3) *::text, td:nth-child(3)::text").get(default="").strip()
    periodicidad = r.css("td:nth-child(4) *::text, td:nth-child(4)::text").get(default="").strip()
    vig_txt  = r.css("td:nth-child(5) *::text, td:nth-child(5)::text").get(default="").strip()

    # normalización rápida
    num = (valor_txt.replace("$","").replace("COP","").replace(".","").replace(",","")).strip()
    try:
        amount = float(num)
    except:
        amount = None

    yield {
        "product_ref": producto,
        "concept": concepto,
        "amount": amount,
        "currency": "COP",
        "periodicity": periodicidad,
        "effective_from": vig_txt,
        "source_url": response.url,
    }

# Fallback PDF
for a in response.css('a[href$=".pdf"], a:contains("PDF"), a:contains("tarifas"), a:contains("comisiones")'):
    yield {"url_pdf": response.urljoin(a.attrib.get("href","")), "source_url": response.url}

