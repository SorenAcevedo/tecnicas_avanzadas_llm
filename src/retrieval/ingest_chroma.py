"""
Simple ingestion script to build a Chroma DB from processed text files.
- Splits documents into lightweight chunks.
- Stores text + metadata into a persistent Chroma collection.

Run (opcional):
    python -m src.retrieval.ingest_chroma
"""

import os
import time
from dotenv import load_dotenv
from pathlib import Path
from typing import Iterable, List, Dict, Optional
import argparse

from .vector_store import get_chroma, DEFAULT_COLLECTION, DEFAULT_PERSIST_DIR

# Source files (already produced by ETL)
PROCESSED_DIR = Path("data/processed")
SOURCES = [
    (PROCESSED_DIR / "context_colgate.txt", {"type": "product", "brand": "colgate"}),
    (PROCESSED_DIR / "context_palmolive.txt", {"type": "product", "brand": "palmolive"}),
    (PROCESSED_DIR / "company_context.txt", {"type": "company"}),
    (PROCESSED_DIR / "context_youtube.txt", {"type": "youtube"}),
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_paragraphs(text: str) -> List[str]:
    # Basic split by blank lines
    paras: List[str] = []
    current: List[str] = []
    for line in text.splitlines():
        if line.strip():
            current.append(line)
        else:
            if current:
                paras.append(" ".join(current).strip())
                current = []
    if current:
        paras.append(" ".join(current).strip())
    return paras


def chunk_text(paragraphs: List[str], max_chars: int = 1200, overlap: int = 150) -> List[str]:
    chunks: List[str] = []
    buff = ""
    for para in paragraphs:
        if not para:
            continue
        if len(buff) + len(para) + 1 <= max_chars:
            buff = (buff + " " + para).strip()
        else:
            if buff:
                chunks.append(buff)
            # start new window with overlap from previous buff tail
            if overlap and chunks:
                tail = chunks[-1][-overlap:]
                buff = (tail + " " + para).strip()
            else:
                buff = para
    if buff:
        chunks.append(buff)
    return chunks


def iter_documents(limit: Optional[int] = None) -> Iterable[Dict]:
    for path, base_meta in SOURCES:
        if not path.exists():
            continue
        text = read_text(path)
        paras = split_paragraphs(text)
        # adaptive chunking per type for better recall/precision
        t = base_meta.get("type")
        if t == "company":
            max_chars, overlap = 700, 120
        elif t == "youtube":
            max_chars, overlap = 900, 120
        else:  # products
            max_chars, overlap = 1200, 150
        for i, chunk in enumerate(chunk_text(paras, max_chars=max_chars, overlap=overlap)):
            meta = {
                **base_meta,
                "source": str(path),
                "position": i,
            }
            yield {"text": chunk, "metadata": meta}
            if limit is not None:
                limit -= 1
                if limit <= 0:
                    return


def main() -> None:
    # Ensure .env variables (e.g., GOOGLE_API_KEY, VECTOR_DB_* ) are available
    load_dotenv(override=True)

    parser = argparse.ArgumentParser(description="Ingest processed texts into Chroma.")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max number of chunks to ingest (0 = no limit)")
    parser.add_argument("--batch", type=int, default=48,
                        help="Batch size for upserting/embedding texts (default 48)")
    parser.add_argument("--sleep", type=float, default=1.5,
                        help="Seconds to sleep between batches to avoid rate limits (default 1.5)")
    args = parser.parse_args()

    vs = get_chroma(collection=DEFAULT_COLLECTION, persist_dir=DEFAULT_PERSIST_DIR)

    # Add documents
    texts = []
    metadatas = []
    ids = []
    limit = None if args.limit == 0 else args.limit
    for idx, doc in enumerate(iter_documents(limit=limit)):
        texts.append(doc["text"])
        metadatas.append(doc["metadata"])
        ids.append(f"doc-{idx}")

    if not texts:
        print("No documents found to ingest.")
        return

    # Upsert in batches
    batch = max(1, int(args.batch))
    total = len(texts)
    for i in range(0, total, batch):
        j = min(i + batch, total)
        vs.add_texts(texts=texts[i:j], metadatas=metadatas[i:j], ids=ids[i:j])
        if args.sleep > 0 and j < total:
            time.sleep(args.sleep)
    print(f"Ingested {len(texts)} chunks into collection '{DEFAULT_COLLECTION}' at '{DEFAULT_PERSIST_DIR}'.")


if __name__ == "__main__":
    main()
