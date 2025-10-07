"""
RAG Knowledge System - Scalable Enterprise Chatbot Solution

This package provides a complete RAG (Retrieval-Augmented Generation) system
for building enterprise chatbots based on scraped knowledge bases.

Key Features:
- Scalable web scraping with Scrapy
- Advanced text processing and chunking
- Multiple vector database backends
- LLM abstraction layer (OpenAI, Anthropic, Ollama)
- Real-time chatbot interface with Streamlit
- Comprehensive monitoring and logging

Architecture:
- Clean Architecture with Domain-Driven Design
- Microservices-ready with Docker containerization
- Asynchronous processing with Celery
- Professional development workflows with uv and make

Author: RAG Knowledge Team
License: MIT
"""

__version__ = "1.0.0"
__author__ = "RAG Knowledge Team"
__email__ = "team@ragknowledge.com"
__license__ = "MIT"

# Version info
VERSION_INFO = tuple(map(int, __version__.split(".")))

# Package metadata
PACKAGE_NAME = "rag-knowledge-system"
PACKAGE_DESCRIPTION = "Scalable RAG Knowledge System for Enterprise Chatbots"

# Export main components
from src.core.config.settings import settings
from src.core.logging.logger import get_logger

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "VERSION_INFO",
    "PACKAGE_NAME", 
    "PACKAGE_DESCRIPTION",
    "settings",
    "get_logger",
]