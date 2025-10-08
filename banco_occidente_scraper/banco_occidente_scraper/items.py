# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BancoOccidenteItem(scrapy.Item):
    # Información general de la página
    titulo = scrapy.Field()
    descripcion = scrapy.Field()
    url = scrapy.Field()
    
    # Contenido principal (texto corrido - para compatibilidad)
    texto_principal = scrapy.Field()
    subtitulos = scrapy.Field()
    
    # Contenido estructurado por secciones
    contenido_estructurado = scrapy.Field()  # [{"titulo": "H1/H2", "nivel": 1-6, "contenido": "texto"}]
    
    # Enlaces y referencias
    enlaces_internos = scrapy.Field()
    enlaces_externos = scrapy.Field()
    
    # Metadata
    fecha_scraping = scrapy.Field()
    imagenes = scrapy.Field()
