scrape-palmolive:
	uv run python src/scraping/palmolive_productos.py

scrape-colgate:
	uv run python src/scraping/colgate_productos.py

scrape-all: scrape-palmolive scrape-colgate

preprocess:
	uv run python src/processing/preprocessing.py

txt-products-preprocess:
	uv run python src/processing/plain_products_processing.py

txt-youtube-preprocess:
	uv run python src/processing/plain_youtube_processing.py

txt-company-preprocess:
	uv run python src/processing/plain_company_processing.py

txt-preprocess: txt-products-preprocess txt-youtube-preprocess txt-company-preprocess

chunk:
	uv run python src/processing/chunking.py

start:
	uv run streamlit run app.py