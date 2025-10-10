# Banco de Occidente — Selectores iniciales (Sucursales / branches)

## Fuente
- URL:(https://www.bancodeoccidente.com.co/BuscadordePuntosOccidente/)
## Estructura esperada (CSS para Scrapy)
> Nota: muchos bancos cargan sucursales vía JS o un endpoint JSON. Si ves que el HTML está vacío, revisa el panel “Network” del navegador y documenta la URL del API (GET /sucursales?...).

- **Tarjeta de sucursal**: `.branch-card, .office-card, .sucursal, li.branch`
- **Nombre**: `.branch-name, .title, h3, h2`
- **Dirección**: `.branch-address, .address`
- **Horario**: `.branch-hours, .hours, .schedule`
- **Teléfonos**: `.branch-phone, .phone, a[href^="tel:"]`
- **Ciudad (si aparece por grupo)**: encabezado o filtro activo `.city, .filter-city`

## Mapeo → schema `branches`
- `city`         ← ciudad visible o del grupo (si no aparece, intentar inferir desde la URL o dejar `null`)
- `branch_name`  ← texto del nombre
- `address`      ← texto de la dirección
- `hours`        ← texto limpio del horario
- `phones`       ← lista de teléfonos detectados (`a[href^="tel:"]` → extraer número)
- `source_url`   ← `response.url`
- `extracted_at` ← timestamp

## Fallback: API/JSON
Si detectas carga vía API:
- Documenta aquí la URL del endpoint (ej. `/api/branches?city=...`)
- Campos típicos del JSON: `name, address, city, phones, lat, lon, hours`
- En Scrapy, parsea `response.json()` y emite los campos mapeados.

## Ejemplo mínimo (HTML)
```python
for it in response.css(".branch-card, .office-card, .sucursal, li.branch"):
    name = it.css(".branch-name, .title, h3, h2::text").get(default="").strip()
    address = it.css(".branch-address, .address::text").get(default="").strip()
    hours = " ".join(x.strip() for x in it.css(".branch-hours, .hours, .schedule *::text").getall() if x.strip())
    phones = [p.attrib.get("href","").replace("tel:","").strip() for p in it.css('a[href^="tel:"]')]
    yield {
        "branch_name": name,
        "address": address,
        "hours": hours or None,
        "phones": phones or [],
        "source_url": response.url,
    }
