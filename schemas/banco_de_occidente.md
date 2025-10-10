# Banco de Occidente – Esquemas de scraping

## faq
Cada pregunta frecuente o artículo de ayuda será **un registro**.

| Campo | Tipo | Descripción |
|--------|------|-------------|
| id | string | Identificador único, ej. `banco_de_occidente:faq:slug_pregunta` |
| question | string | Texto completo de la pregunta |
| answer | string | Respuesta en texto plano (sin etiquetas HTML) |
| url | string | URL original de la página |
| category | string | Sección o categoría (ej. "cuentas", "tarjetas") |
| extracted_at | datetime | Fecha y hora de extracción en formato ISO |

---

## rates
Cada registro corresponde a **una tasa de interés** publicada en el sitio o PDF oficial.

| Campo | Tipo | Descripción |
|--------|------|-------------|
| id | string | `banco_de_occidente:producto:EA` |
| product_name | string | Nombre del producto financiero |
| rate_type | string | Tipo de tasa (EA / NMV / otro) |
| value | number | Valor numérico, ej. 12.5 |
| effective_from | date | Fecha de inicio de vigencia |
| source_url | string | Página o PDF donde se obtuvo |
| extracted_at | datetime | Fecha de extracción |

---

## fees
Cada fila representa **una tarifa o comisión**.

| Campo | Tipo | Descripción |
|--------|------|-------------|
| id | string | `banco_de_occidente:producto:concepto` |
| product_ref | string | Producto al que pertenece la tarifa |
| concept | string | Ej. “cuota de manejo” |
| amount | number | Valor en pesos colombianos |
| currency | string | Código ISO-4217 (usualmente COP) |
| periodicity | string | Periodicidad: mensual / por_transacción |
| effective_from | date | Fecha de inicio de vigencia |
| source_url | string | URL de la fuente o PDF |
| extracted_at | datetime | Fecha de extracción |

---

## branches
Cada registro describe **una sucursal u oficina**.

| Campo | Tipo | Descripción |
|--------|------|-------------|
| id | string | `banco_de_occidente:ciudad:slug_sucursal` |
| city | string | Ciudad |
| branch_name | string | Nombre oficial de la sucursal |
| address | string | Dirección |
| hours | string | Horario de atención |
| phones | array | Lista de teléfonos |
| source_url | string | URL de la fuente |
| extracted_at | datetime | Fecha de extracción |

---

## news
Cada registro representa **una noticia, comunicado o entrada de blog oficial**.

| Campo | Tipo | Descripción |
|--------|------|-------------|
| id | string | Identificador único del artículo |
| title | string | Título o encabezado |
| summary | string | Resumen corto |
| body | string | Texto completo del artículo |
| url | string | URL del comunicado |
| published_at | date | Fecha de publicación |
| source_url | string | Página padre |
| extracted_at | datetime | Fecha de extracción |
