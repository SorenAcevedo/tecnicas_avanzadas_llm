"""
Embeddings provider (Google Generative AI / Gemini) via langchain-google-genai.
"""

import os
from typing import Optional

from langchain_core.embeddings import Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings


def get_embeddings(model: Optional[str] = None) -> Embeddings:
    """Return a configured Google Gemini embeddings instance.

    Args:
        model: Optional explicit embeddings model id.

    Returns:
        A LangChain Embeddings implementation backed by Google Generative AI.
    """
    model = model or os.getenv("RAG_EMBEDDINGS_MODEL", "models/text-embedding-004")
    task_type = os.getenv("RAG_EMBEDDINGS_TASK")  # e.g., "SEMANTIC_SIMILARITY"
    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY is not set. Configure it in your .env")
    return GoogleGenerativeAIEmbeddings(model=model, task_type=task_type)
