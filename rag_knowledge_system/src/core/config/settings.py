"""
Centralized configuration management for RAG Knowledge System.

This module provides a unified configuration system using Pydantic Settings
for type validation, environment variable management, and configuration loading.
"""

import os
from typing import Optional, List, Dict, Any
from pathlib import Path
from pydantic import BaseSettings, Field, validator
from enum import Enum


class Environment(str, Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class ChunkingStrategy(str, Enum):
    """Chunking strategies for text processing"""
    RECURSIVE_CHARACTER = "recursive_character"
    SEMANTIC = "semantic"
    MARKDOWN = "markdown"
    HTML = "html"
    TOKEN = "token"


class VectorDBProvider(str, Enum):
    """Supported vector database providers"""
    CHROMADB = "chromadb"
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"
    FAISS = "faiss"


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"


class DatabaseSettings(BaseSettings):
    """Database configuration"""
    url: str = Field(default="postgresql://user:password@localhost:5432/rag_knowledge_db")
    redis_url: str = Field(default="redis://localhost:6379/0")
    
    class Config:
        env_prefix = "DATABASE_"


class ScrapingSettings(BaseSettings):
    """Web scraping configuration"""
    user_agent: str = Field(default="RAG-Knowledge-Bot 1.0")
    delay: float = Field(default=1.0, ge=0.1)
    concurrent_requests: int = Field(default=8, ge=1, le=32)
    autothrottle_enabled: bool = Field(default=True)
    use_proxies: bool = Field(default=False)
    proxy_list_url: Optional[str] = None
    proxy_username: Optional[str] = None
    proxy_password: Optional[str] = None
    
    class Config:
        env_prefix = "SCRAPY_"


class EmbeddingSettings(BaseSettings):
    """Embedding model configuration"""
    model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    dimension: int = Field(default=384, ge=128)
    batch_size: int = Field(default=32, ge=1)
    
    class Config:
        env_prefix = "EMBEDDING_"


class ChunkingSettings(BaseSettings):
    """Text chunking configuration"""
    size: int = Field(default=1000, ge=100, le=8000)
    overlap: int = Field(default=200, ge=0)
    strategy: ChunkingStrategy = Field(default=ChunkingStrategy.RECURSIVE_CHARACTER)
    
    @validator('overlap')
    def validate_overlap(cls, v, values):
        if 'size' in values and v >= values['size']:
            raise ValueError('Overlap must be less than chunk size')
        return v
    
    class Config:
        env_prefix = "CHUNK_"


class VectorStoreSettings(BaseSettings):
    """Vector store configuration"""
    provider: VectorDBProvider = Field(default=VectorDBProvider.CHROMADB)
    
    # ChromaDB
    chroma_persist_directory: str = Field(default="./data/chroma_db")
    chroma_collection_name: str = Field(default="knowledge_base")
    
    # Pinecone
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    pinecone_index_name: str = Field(default="rag-knowledge-index")
    
    # Weaviate
    weaviate_url: str = Field(default="http://localhost:8080")
    weaviate_class_name: str = Field(default="Document")
    
    class Config:
        env_prefix = ""


class OpenAISettings(BaseSettings):
    """OpenAI configuration"""
    api_key: Optional[str] = None
    model: str = Field(default="gpt-4")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=1)
    
    class Config:
        env_prefix = "OPENAI_"


class AnthropicSettings(BaseSettings):
    """Anthropic configuration"""
    api_key: Optional[str] = None
    model: str = Field(default="claude-3-sonnet-20240229")
    
    class Config:
        env_prefix = "ANTHROPIC_"


class OllamaSettings(BaseSettings):
    """Ollama configuration"""
    base_url: str = Field(default="http://localhost:11434")
    model: str = Field(default="llama3")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    
    class Config:
        env_prefix = "OLLAMA_"


class LLMSettings(BaseSettings):
    """LLM configuration container"""
    default_provider: LLMProvider = Field(default=LLMProvider.OPENAI)
    openai: OpenAISettings = OpenAISettings()
    anthropic: AnthropicSettings = AnthropicSettings()
    ollama: OllamaSettings = OllamaSettings()


class APISettings(BaseSettings):
    """API server configuration"""
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, ge=1024, le=65535)
    reload: bool = Field(default=True)
    workers: int = Field(default=1, ge=1)
    
    class Config:
        env_prefix = "API_"


class StreamlitSettings(BaseSettings):
    """Streamlit configuration"""
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8501, ge=1024, le=65535)
    
    class Config:
        env_prefix = "STREAMLIT_"


class SecuritySettings(BaseSettings):
    """Security configuration"""
    secret_key: str = Field(default="your_secret_key_here")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30, ge=1)
    rate_limit_requests: int = Field(default=100, ge=1)
    rate_limit_period: int = Field(default=3600, ge=1)
    
    class Config:
        env_prefix = ""


class MonitoringSettings(BaseSettings):
    """Monitoring and logging configuration"""
    sentry_dsn: Optional[str] = None
    prometheus_port: int = Field(default=9090, ge=1024, le=65535)
    enable_tracing: bool = Field(default=True)
    
    class Config:
        env_prefix = ""


class StorageSettings(BaseSettings):
    """File storage configuration"""
    data_directory: Path = Field(default=Path("./data"))
    raw_data_dir: Path = Field(default=Path("./data/raw"))
    processed_data_dir: Path = Field(default=Path("./data/processed"))
    embeddings_data_dir: Path = Field(default=Path("./data/embeddings"))
    models_dir: Path = Field(default=Path("./data/models"))
    cache_dir: Path = Field(default=Path("./data/cache"))
    logs_dir: Path = Field(default=Path("./logs"))
    
    @validator('*', pre=True)
    def validate_paths(cls, v):
        if isinstance(v, str):
            return Path(v)
        return v
    
    class Config:
        env_prefix = ""


class CelerySettings(BaseSettings):
    """Celery configuration"""
    broker_url: str = Field(default="redis://localhost:6379/1")
    result_backend: str = Field(default="redis://localhost:6379/2")
    task_serializer: str = Field(default="json")
    result_serializer: str = Field(default="json")
    
    class Config:
        env_prefix = "CELERY_"


class Settings(BaseSettings):
    """Main application settings"""
    
    # Environment
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=True)
    log_level: str = Field(default="INFO")
    
    # Component settings
    database: DatabaseSettings = DatabaseSettings()
    scraping: ScrapingSettings = ScrapingSettings()
    embedding: EmbeddingSettings = EmbeddingSettings()
    chunking: ChunkingSettings = ChunkingSettings()
    vector_store: VectorStoreSettings = VectorStoreSettings()
    llm: LLMSettings = LLMSettings()
    api: APISettings = APISettings()
    streamlit: StreamlitSettings = StreamlitSettings()
    security: SecuritySettings = SecuritySettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    storage: StorageSettings = StorageSettings()
    celery: CelerySettings = CelerySettings()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.storage.data_directory,
            self.storage.raw_data_dir,
            self.storage.processed_data_dir,
            self.storage.embeddings_data_dir,
            self.storage.models_dir,
            self.storage.cache_dir,
            self.storage.logs_dir,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @property
    def is_development(self) -> bool:
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_testing(self) -> bool:
        return self.environment == Environment.TESTING
    
    def get_llm_config(self, provider: Optional[LLMProvider] = None) -> Dict[str, Any]:
        """Get LLM configuration for specified provider"""
        provider = provider or self.llm.default_provider
        
        if provider == LLMProvider.OPENAI:
            return {
                "provider": "openai",
                "api_key": self.llm.openai.api_key,
                "model": self.llm.openai.model,
                "temperature": self.llm.openai.temperature,
                "max_tokens": self.llm.openai.max_tokens,
            }
        elif provider == LLMProvider.ANTHROPIC:
            return {
                "provider": "anthropic",
                "api_key": self.llm.anthropic.api_key,
                "model": self.llm.anthropic.model,
            }
        elif provider == LLMProvider.OLLAMA:
            return {
                "provider": "ollama",
                "base_url": self.llm.ollama.base_url,
                "model": self.llm.ollama.model,
                "temperature": self.llm.ollama.temperature,
            }
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    def get_vector_store_config(self) -> Dict[str, Any]:
        """Get vector store configuration"""
        if self.vector_store.provider == VectorDBProvider.CHROMADB:
            return {
                "provider": "chromadb",
                "persist_directory": self.vector_store.chroma_persist_directory,
                "collection_name": self.vector_store.chroma_collection_name,
            }
        elif self.vector_store.provider == VectorDBProvider.PINECONE:
            return {
                "provider": "pinecone",
                "api_key": self.vector_store.pinecone_api_key,
                "environment": self.vector_store.pinecone_environment,
                "index_name": self.vector_store.pinecone_index_name,
            }
        elif self.vector_store.provider == VectorDBProvider.WEAVIATE:
            return {
                "provider": "weaviate",
                "url": self.vector_store.weaviate_url,
                "class_name": self.vector_store.weaviate_class_name,
            }
        else:
            raise ValueError(f"Unsupported vector store provider: {self.vector_store.provider}")


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance"""
    return settings