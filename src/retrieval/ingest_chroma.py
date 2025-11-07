"""
Ingestion script to build a Chroma DB from processed text files.

Uses RecursiveCharacterTextSplitter for semantically coherent chunking.
Adaptive chunk sizes based on document type (company, product, youtube).

Run:
    python -m src.retrieval.ingest_chroma
"""

import sys
from pathlib import Path
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

from .vector_store import get_chroma

DEFAULT_COLLECTION = 'colgate_palmolive_kb_gemini_full'
VECTOR_DB_PATH: str = "./data/vector_db"
PROCESSED_DIR = Path("data/processed")
SOURCES = [
    (PROCESSED_DIR / "context_colgate.txt", {"type": "product", "brand": "colgate"}),
    (PROCESSED_DIR / "context_palmolive.txt", {"type": "product", "brand": "palmolive"}),
    (PROCESSED_DIR / "company_context.txt", {"type": "company"}),
    (PROCESSED_DIR / "context_youtube.txt", {"type": "youtube"}),
]


def get_text_splitter(doc_type: str) -> RecursiveCharacterTextSplitter:
    configs = {
        "company": {"chunk_size": 800, "chunk_overlap": 100},
        "youtube": {"chunk_size": 1000, "chunk_overlap": 150},
        "product": {"chunk_size": 1500, "chunk_overlap": 200},
    }
    config = configs.get(doc_type, configs["product"])
    
    return RecursiveCharacterTextSplitter(
        chunk_size=config["chunk_size"],
        chunk_overlap=config["chunk_overlap"],
        separators=["\n\n", "\n", ". ", ", ", " ", ""],
        length_function=len,
        is_separator_regex=False,
    )


def get_all_chunks() -> tuple[List[str], List[dict]]:
    texts = []
    metadatas = []
    
    for path, base_meta in SOURCES:
        if not path.exists():
            continue
        
        text = path.read_text(encoding="utf-8")
        doc_type = base_meta.get("type", "product")
        splitter = get_text_splitter(doc_type)
        chunks = splitter.split_text(text)
        
        for i, chunk in enumerate(chunks):
            texts.append(chunk)
            metadatas.append({
                **base_meta,
                "source": str(path),
                "position": i,
                "chunk_size": len(chunk),
            })
    
    return texts, metadatas


def main() -> None:
    print("Loading and chunking documents...")
    texts, metadatas = get_all_chunks()
    
    if not texts:
        print("No documents found.")
        return
    
    print(f"Generated {len(texts)} chunks. Ingesting into Chroma...")
    
    vectorstore = get_chroma(
        collection=DEFAULT_COLLECTION,
        persist_dir=VECTOR_DB_PATH
    )
    
    vectorstore.add_texts(texts=texts, metadatas=metadatas)
    
    print(f"Successfully ingested {len(texts)} chunks into '{DEFAULT_COLLECTION}'.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
