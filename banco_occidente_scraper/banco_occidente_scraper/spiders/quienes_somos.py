import scrapy
from datetime import datetime
from banco_occidente_scraper.items import BancoOccidenteItem
from urllib.parse import urljoin, urlparse


class QuienesSomosSpider(scrapy.Spider):
    name = "quienes_somos"
    allowed_domains = ["bancodeoccidente.com.co"]
    start_urls = ["https://www.bancodeoccidente.com.co/wps/portal/banco-de-occidente/bancodeoccidente/quienes-somos/quienessomos"]
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    def parse(self, response):
        item = BancoOccidenteItem()
        
        # Información básica de la página
        item['url'] = response.url
        item['titulo'] = response.css('title::text').get() or response.css('h1::text').get()
        item['descripcion'] = response.css('meta[name="description"]::attr(content)').get()
        item['fecha_scraping'] = datetime.now().isoformat()
        
        # Extraer texto principal
        # Buscar contenido en diferentes selectores comunes
        texto_paragrafos = response.css('p::text').getall()
        texto_divs = response.css('div.contenido::text, div.texto::text, div.content::text').getall()
        item['texto_principal'] = ' '.join(texto_paragrafos + texto_divs).strip()
        
        # Extraer subtítulos
        subtitulos = response.css('h1::text, h2::text, h3::text, h4::text').getall()
        item['subtitulos'] = [titulo.strip() for titulo in subtitulos if titulo.strip()]
        
        # Extraer enlaces internos y externos
        enlaces = response.css('a::attr(href)').getall()
        enlaces_internos = []
        enlaces_externos = []
        
        for enlace in enlaces:
            if enlace:
                enlace_completo = urljoin(response.url, enlace)
                parsed_url = urlparse(enlace_completo)
                
                if parsed_url.netloc == 'www.bancodeoccidente.com.co' or parsed_url.netloc == 'bancodeoccidente.com.co':
                    enlaces_internos.append(enlace_completo)
                elif parsed_url.netloc:  # Enlaces externos (que tienen dominio)
                    enlaces_externos.append(enlace_completo)
        
        item['enlaces_internos'] = list(set(enlaces_internos))  # Eliminar duplicados
        item['enlaces_externos'] = list(set(enlaces_externos))  # Eliminar duplicados
        
        # Extraer imágenes
        imagenes = response.css('img::attr(src)').getall()
        item['imagenes'] = [urljoin(response.url, img) for img in imagenes if img]
        
        self.logger.info(f'Scrapeado: {item["titulo"]}')
        
        yield item
        
        # Si quieres seguir enlaces internos para hacer scraping más profundo
        # (opcional - comentado para no hacer scraping masivo)
        # for enlace in enlaces_internos[:5]:  # Limitar a 5 enlaces
        #     yield response.follow(enlace, self.parse)
