# Banco de Occidente — Selectores iniciales (FAQ)

## Fuente
- URL: (https://webavc.bancodeoccidente.com.co/wps/portal/banco-de-occidente/bancodeoccidente/canales-servicios/contactanos/preguntas-frecuentes/!ut/p/z1/04_Sj9CPykssy0xPLMnMz0vMAfIjo8zifQIszTwsTQx8DJxDzA0c_bw8vExdLY3NAkz1w1EVuLsHugAVGDkaBjs7GQcYGuhHEaPfAAdwJFI_HgVR-I0P14_Ca4WvOboCLF5EU-BqZmHgaO5hYOTrE2BgEGAIVYDHFQW5oaERBpme6Y6KigAW8dp1/dz/d5/L2dBISEvZ0FBIS9nQSEh/)
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

