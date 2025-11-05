scrape-palmolive:
	uv run python etl/extract/palmolive_productos.py

scrape-colgate:
	uv run python etl/extract/colgate_productos.py

scrape-all: scrape-palmolive scrape-colgate

preprocess:
	uv run python etl/transform/preprocessing.py

txt-products-preprocess:
	uv run python etl/transform/plain_products_processing.py

txt-youtube-preprocess:
	uv run python etl/transform/plain_youtube_processing.py

txt-company-preprocess:
	uv run python etl/transform/plain_company_processing.py

txt-preprocess: txt-products-preprocess txt-youtube-preprocess txt-company-preprocess

chunk:
	uv run python src/processing/chunking.py

start: db-restart
	uv run main.py

# ====================================
# Database Commands (PostgreSQL)
# ====================================

# Crear y ejecutar contenedor PostgreSQL para memoria del chatbot
db-start:
	docker run -d \
		--name uao_llm \
		-e POSTGRES_USER=student \
		-e POSTGRES_PASSWORD=12345678 \
		-e POSTGRES_DB=uao_llm \
		-p 5442:5432 \
		postgres:16-alpine

# Detener el contenedor PostgreSQL
db-stop:
	docker stop uao_llm

# Iniciar el contenedor PostgreSQL existente
db-restart:
	docker start uao_llm

# Eliminar el contenedor PostgreSQL
db-remove:
	docker rm -f uao_llm

# Ver logs del contenedor PostgreSQL
db-logs:
	docker logs -f uao_llm

# Conectarse a la base de datos con psql
db-shell:
	docker exec -it uao_llm psql -U student -d uao_llm

# Resetear la base de datos (eliminar y crear de nuevo)
db-reset: db-remove db-start
	@echo "Esperando que PostgreSQL inicie..."
	@timeout /t 3 /nobreak > nul
	@echo "Base de datos reseteada exitosamente"

# Verificar estado del contenedor
db-status:
	docker ps -a --filter name=uao_llm