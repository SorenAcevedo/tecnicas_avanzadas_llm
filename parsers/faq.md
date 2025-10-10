# Banco de Occidente — Selectores iniciales (FAQ)

## Fuente
- URL: (pega aquí la URL exacta de la sección de FAQ/ayuda del banco)
- Nota: si luego cambia, actualizamos este archivo. Este doc guía a Scrapy; no es código.

## Estructura esperada (CSS para Scrapy)
- **Item FAQ (contenedor):**
  - `.accordion-item, .faq-item`
- **Pregunta:**
  - `.accordion-header::text, .faq-question::text`
- **Respuesta (texto plano):**
  - `.accordion-body *::text, .faq-answer *::text`

## Mapeo → schema `faq`
- `question`  ← texto de **Pregunta**
- `answer`    ← join de todos los textos en **Respuesta**
- `url`       ← `response.url` (página actual)
- `category`  ← si hay pestañas/secciones visibles, captura su texto; si no, `null`
- `extracted_at` ← timestamp al momento de extracción

## Fallbacks
- Si no hay `.accordion-item`, probar `.collapse-item`, `.card`, o buscar títulos con `h2,h3:contains("Preguntas")`.
- Si la respuesta trae HTML complejo, extraer con `*::text` y colapsar espacios.

## Ejemplo mínimo (solo referencia)
```python
for it in response.css(".accordion-item, .faq-item"):
    pregunta = it.css(".accordion-header::text, .faq-question::text").get(default="").strip()
    respuesta = " ".join(x.strip() for x in it.css(".accordion-body *::text, .faq-answer *::text").getall() if x.strip())
    yield {
        "id": "",  # el equipo definirá el slug
        "question": pregunta,
        "answer": respuesta,
        "url": response.url,
    }

