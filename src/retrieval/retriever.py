"""
Query wrapper for Chroma using Gemini embeddings.
"""

import os
from typing import List, Dict, Optional

try:
    from src.config.logger import get_logger
    _logger = get_logger(__name__)
except Exception:  # fallback if logger isn't available early
    _logger = None

from .vector_store import get_chroma
DEFAULT_COLLECTION = 'colgate_palmolive_kb_gemini_full'
DEFAULT_PERSIST_DIR: str = "./data/vector_db"

def search(
    query: str,
    top_k: int = 4,
    filter_type: Optional[str] = None,
) -> List[Dict]:
    """Search the Chroma store, returning metadata + text for top results.

    Args:
        query: User question
        top_k: Number of results
        filter_type: Optional metadata filter on type

    Returns:
        List of dicts: {"text": str, "metadata": dict, "score": float}
    """
    chroma = get_chroma(collection=DEFAULT_COLLECTION, persist_dir=DEFAULT_PERSIST_DIR)

    filt = {"type": filter_type} if filter_type else None
    results = chroma.similarity_search_with_score(query, k=top_k, filter=filt)

    output: List[Dict] = []
    for doc, score in results:
        output.append({
            "text": doc.page_content,
            "metadata": doc.metadata,
            "score": float(score),
        })
    # Debug trace if enabled
    if os.getenv("RAG_DEBUG"):
        try:
            if _logger:
                _logger.debug(
                    "RAG search | collection=%s | top_k=%s | filter=%s | results=%s | first_sources=%s",
                    DEFAULT_COLLECTION,
                    top_k,
                    filt,
                    len(output),
                    [o.get("metadata", {}).get("source") for o in output[:3]],
                )
            else:
                print(
                    f"[RAG_DEBUG] collection={DEFAULT_COLLECTION} top_k={top_k} filter={filt} results={len(output)}"
                )
        except Exception:
            pass
    return output
