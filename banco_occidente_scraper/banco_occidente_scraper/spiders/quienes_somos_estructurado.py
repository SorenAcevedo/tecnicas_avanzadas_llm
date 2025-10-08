import scrapy
from datetime import datetime
from banco_occidente_scraper.items import BancoOccidenteItem
from urllib.parse import urljoin, urlparse


class QuienesSomosEstructuradoSpider(scrapy.Spider):
    name = "quienes_somos_estructurado"
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
        
        # Extraer contenido estructurado
        contenido_estructurado = self.extraer_contenido_con_titulos(response)
        item['contenido_estructurado'] = contenido_estructurado
        
        # Mantener compatibilidad con versión anterior
        texto_paragrafos = response.css('p::text').getall()
        texto_divs = response.css('div.contenido::text, div.texto::text, div.content::text').getall()
        item['texto_principal'] = ' '.join(texto_paragrafos + texto_divs).strip()
        
        # Extraer subtítulos
        subtitulos = response.css('h1::text, h2::text, h3::text, h4::text, h5::text, h6::text').getall()
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
        
        self.logger.info(f'Scrapeado estructurado: {item["titulo"]}')
        self.logger.info(f'Secciones encontradas: {len(contenido_estructurado)}')
        
        yield item

    def extraer_contenido_con_titulos(self, response):
        """
        Extrae el contenido manteniendo la jerarquía de títulos
        Devuelve una lista de diccionarios con título, nivel y contenido
        """
        contenido_estructurado = []
        
        # Buscar todos los elementos que pueden ser títulos o contenido
        elementos = response.css('h1, h2, h3, h4, h5, h6, p, div')
        
        titulo_actual = None
        nivel_actual = None
        contenido_acumulado = []
        
        for elemento in elementos:
            # Verificar si es un título (h1, h2, etc.)
            tag_name = elemento.root.tag.lower() if hasattr(elemento.root, 'tag') else ''
            
            if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                # Si ya teníamos un título anterior, guardarlo con su contenido
                if titulo_actual is not None:
                    contenido_estructurado.append({
                        'titulo': titulo_actual,
                        'nivel': nivel_actual,
                        'contenido': ' '.join(contenido_acumulado).strip()
                    })
                
                # Nuevo título
                titulo_texto = elemento.css('::text').get()
                if titulo_texto and titulo_texto.strip():
                    titulo_actual = titulo_texto.strip()
                    nivel_actual = int(tag_name[1])  # h1->1, h2->2, etc.
                    contenido_acumulado = []
            
            elif tag_name in ['p', 'div']:
                # Es contenido, extraer texto
                textos = elemento.css('::text').getall()
                texto_limpio = ' '.join([t.strip() for t in textos if t.strip()])
                
                if texto_limpio:
                    contenido_acumulado.append(texto_limpio)
        
        # Agregar el último título y contenido si existe
        if titulo_actual is not None:
            contenido_estructurado.append({
                'titulo': titulo_actual,
                'nivel': nivel_actual,
                'contenido': ' '.join(contenido_acumulado).strip()
            })
        
        # Si no se encontraron títulos, intentar una extracción más básica
        if not contenido_estructurado:
            # Buscar secciones por divs con clases comunes
            secciones = response.css('div[class*="section"], div[class*="content"], section, article')
            
            for i, seccion in enumerate(secciones):
                titulo_en_seccion = seccion.css('h1::text, h2::text, h3::text, h4::text').get()
                contenido_seccion = ' '.join(seccion.css('p::text, div::text').getall()).strip()
                
                if contenido_seccion:  # Solo agregar si tiene contenido
                    contenido_estructurado.append({
                        'titulo': titulo_en_seccion or f'Sección {i+1}',
                        'nivel': 2 if titulo_en_seccion else 0,
                        'contenido': contenido_seccion
                    })
        
        # Filtrar secciones vacías
        contenido_estructurado = [
            seccion for seccion in contenido_estructurado 
            if seccion['contenido'] and len(seccion['contenido']) > 10
        ]
        
        return contenido_estructurado