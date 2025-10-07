# ================================
# Multi-stage Dockerfile for RAG Knowledge System
# ================================

# ================================
# BASE IMAGE
# ================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    gcc \
    g++ \
    build-essential \
    pkg-config \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Set working directory
WORKDIR /app

# ================================
# DEPENDENCY STAGE
# ================================
FROM base as dependencies

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies using uv
RUN uv sync --frozen

# ================================
# DEVELOPMENT STAGE
# ================================
FROM dependencies as development

# Install development dependencies
RUN uv sync --extra dev

# Copy source code
COPY . .

# Install the package in editable mode
RUN uv pip install -e .

# Download spaCy models and NLTK data
RUN uv run python -m spacy download en_core_web_sm && \
    uv run python -m spacy download es_core_news_sm && \
    uv run python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

# Create non-root user for development
RUN useradd --create-home --shell /bin/bash ragdev
RUN chown -R ragdev:ragdev /app
USER ragdev

# Expose ports
EXPOSE 8000 8501 8888

# Default command for development
CMD ["uv", "run", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ================================
# PRODUCTION BASE STAGE
# ================================
FROM base as production-base

# Copy only production dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy source code
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/

# Install the package
RUN uv pip install .

# Download required models
RUN uv run python -m spacy download en_core_web_sm && \
    uv run python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

# Create non-root user
RUN useradd --create-home --shell /bin/bash --uid 1000 raguser

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/tmp && \
    chown -R raguser:raguser /app

# Switch to non-root user
USER raguser

# ================================
# PRODUCTION API STAGE
# ================================
FROM production-base as production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uv", "run", "gunicorn", "src.api.main:app", \
     "-w", "4", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]

# ================================
# STREAMLIT STAGE
# ================================
FROM production-base as streamlit

# Health check for Streamlit
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Expose port
EXPOSE 8501

# Command to run Streamlit
CMD ["uv", "run", "streamlit", "run", "src/chatbot/interface/streamlit_app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.fileWatcherType=none"]

# ================================
# SCRAPING STAGE
# ================================
FROM production-base as scraping

# Install additional scraping dependencies
USER root
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome for Selenium
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROME_DRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    wget -N http://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip -P ~/ && \
    unzip ~/chromedriver_linux64.zip -d ~/ && \
    rm ~/chromedriver_linux64.zip && \
    mv ~/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver

# Switch back to non-root user
USER raguser

# Command to run scrapy
CMD ["uv", "run", "scrapy", "crawl", "company_spider"]

# ================================
# TESTING STAGE
# ================================
FROM development as testing

# Run tests
RUN uv run pytest --cov=src --cov-report=html --cov-report=xml

# ================================
# NGINX STAGE (for static file serving)
# ================================
FROM nginx:alpine as nginx

# Copy custom nginx configuration
COPY config/nginx/nginx.conf /etc/nginx/nginx.conf

# Copy SSL certificates (if any)
# COPY config/nginx/ssl/ /etc/nginx/ssl/

# Expose ports
EXPOSE 80 443

# ================================
# DOCUMENTATION STAGE
# ================================
FROM dependencies as docs

# Install documentation dependencies
RUN uv sync --extra dev

# Copy source code
COPY . .

# Build documentation
RUN uv run mkdocs build

# Use nginx to serve documentation
FROM nginx:alpine as docs-serve
COPY --from=docs /app/site /usr/share/nginx/html
EXPOSE 80

# ================================
# CI STAGE (for CI/CD pipelines)
# ================================
FROM dependencies as ci

# Install all dependencies including dev
RUN uv sync --extra dev

# Copy source code
COPY . .

# Run linting and testing
RUN uv run ruff check src tests && \
    uv run mypy src && \
    uv run pytest --cov=src --cov-report=xml --junitxml=junit.xml

# Build the package
RUN uv build

# ================================
# BENCHMARK STAGE
# ================================
FROM production-base as benchmark

# Copy benchmark scripts
COPY scripts/benchmarks/ ./scripts/benchmarks/

# Install benchmarking tools
RUN uv pip install locust pytest-benchmark

# Command to run benchmarks
CMD ["uv", "run", "python", "scripts/benchmarks/run_benchmarks.py"]