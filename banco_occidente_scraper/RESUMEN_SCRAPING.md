# Resumen del Scraping - Banco de Occidente

## Información General
- **URL Scrapeada**: https://www.bancodeoccidente.com.co/wps/portal/banco-de-occidente/bancodeoccidente/quienes-somos/quienessomos
- **Título de la página**: Quienes somos
- **Descripción**: Conoce nuestra historia, misión, visión y valores aquí.
- **Fecha del scraping**: 2025-10-06T21:37:35.825527

## Datos Extraídos

### 1. Información Corporativa
- **Fundación**: El Banco de Occidente nace en Cali el 3 de mayo de 1965
- **Grupo empresarial**: Pertenece a Grupo Aval Acciones y Valores
- **Controlante**: Luis Carlos Sarmiento Angulo
- **Red actual**: Más de 175 oficinas, 18 credicentros y más de 3.093 cajeros automáticos en Colombia
- **Presencia internacional**: Filiales en Panamá y Barbados

### 2. Ejes Estratégicos (4 pilares)
- **Somos líderes**: En segmentos Core con propuestas relevantes, innovadoras y competitivas
- **Somos sostenibles**: Actuando de manera responsable con impacto positivo en la sociedad
- **Somos digitales**: Desarrollando capacidades digitales optimizando procesos
- **Somos deseados**: Creando experiencias memorables para garantizar preferencia

### 3. Valores Corporativos
- **Honestidad**: Generando confianza a través de coherencia
- **Respeto**: Reconociendo y valorando a las personas en su integridad
- **Determinación**: Creencia en capacidad y talento
- **Cooperación**: Trabajando juntos para hacer que las cosas sucedan

### 4. Compromiso Ecológico
- Desde 1984 compromiso con la comunidad a través del trabajo ecológico
- Premio Nacional de Ecología Planeta Azul Banco de Occidente: Agua principio de vida
- Publicaciones anuales de contenido ecológico

## Estructura de Datos Capturados

### Enlaces Internos (Muestra)
- Total de enlaces internos: 168 enlaces únicos
- Incluye productos para personas, empresas, canales digitales, información corporativa

### Enlaces Externos (Muestra) 
- Total de enlaces externos: 29 enlaces únicos
- Incluye redes sociales, entidades regulatorias, aliados estratégicos

### Imágenes
- Total de imágenes: 71 imágenes
- Incluye logos, iconos de servicios, línea de tiempo histórica, redes sociales

### Subtítulos Identificados
- Total: 158 subtítulos
- Categorías: Productos financieros, servicios, canales, segmentos de clientes

## Utilidad de los Datos

Estos datos son valiosos para:
1. **Análisis competitivo**: Entender la estructura de productos y servicios
2. **Research de mercado**: Conocer posicionamiento y propuesta de valor
3. **Análisis de sitio web**: Estructura de navegación y arquitectura de información
4. **Estudios académicos**: Análisis de estrategia digital y corporativa
5. **Benchmarking**: Comparar con otros bancos del sector

## Archivos Generados
- `datos_banco_occidente.json`: Datos en formato JSON compacto
- `datos_banco_occidente_legible.json`: Datos en formato JSON legible
- `RESUMEN_SCRAPING.md`: Este resumen

## Uso del Spider
```bash
# Para ejecutar nuevamente el spider
python -m scrapy crawl quienes_somos -o nuevo_archivo.json

# Para scrapear en formato CSV
python -m scrapy crawl quienes_somos -o datos_banco.csv

# Para scrapear con configuraciones específicas
python -m scrapy crawl quienes_somos -s USER_AGENT="MiBot 1.0" -o datos.json
```