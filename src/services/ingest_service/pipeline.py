import json
import time

from typing import List
from loguru import logger
from src.db.qdrant_db_client import ensure_collection, upsert_products
from src.infrastructure.config import PROJECT_ROOT, EMBEDDING_BATCH_SIZE
from src.infrastructure.llm.embeddings import get_dense_embedder, get_sparse_embedder



def load_catalog():
    path = f"{PROJECT_ROOT}/data/catalog/catalog.json"
    logger.info(f"Loading catalog from {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    logger.info(f"Loaded {len(data)} products")
    return data


def clean_description(text):
    if not text:
        return ""

    lines = text.split("\n")
    return "\n".join(lines)


def product_to_chunk(product):
    return f"""
Product: {product['title']}

Description:
{clean_description(product['description'])}

Price: {product['price']}
"""


def get_product_chunks(products: List):
    logger.info("Building product chunks")

    chunks = [product_to_chunk(p) for p in products]

    logger.info(f"Generated {len(chunks)} chunks")
    return chunks


def get_dense_embeddings(chunks: List, batch_size=EMBEDDING_BATCH_SIZE):
    logger.info("Starting dense embedding generation")

    dense_embedder = get_dense_embedder()
    all_embeddings = []

    start_time = time.time()

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]

        try:
            batch_start = time.time()

            vectors = dense_embedder.embed_documents(batch)
            all_embeddings.extend(vectors)

            elapsed = time.time() - batch_start

            logger.info(
                f"[Dense] Batch {i // batch_size + 1} | "
                f"Processed {i + len(batch)}/{len(chunks)} | "
                f"Batch time: {elapsed:.2f}s"
            )

        except Exception as e:
            logger.error(f"[Dense] Failed batch {i}: {e}")
            continue

    total_time = time.time() - start_time
    logger.success(f"Dense embeddings completed in {total_time:.2f}s")

    return all_embeddings


def get_sparse_embeddings(chunks: List):
    logger.info("Starting sparse embedding generation (BM25)")

    start_time = time.time()

    sparse_embedder = get_sparse_embedder()
    sparse_vectors = list(sparse_embedder.embed(chunks))

    total_time = time.time() - start_time
    logger.success(f"Sparse embeddings completed in {total_time:.2f}s")

    return sparse_vectors


def run_ingest():
    logger.info("Starting ingestion pipeline")

    start_time = time.time()

    products = load_catalog()
    product_chunks = get_product_chunks(products)

    dense_vectors = get_dense_embeddings(product_chunks)
    sparse_vectors = get_sparse_embeddings(product_chunks)

    logger.info("Ensuring Qdrant collection")
    ensure_collection()

    logger.info("Upserting products into Qdrant")
    upsert_products(products, dense_vectors, sparse_vectors)

    total_time = time.time() - start_time
    logger.success(f"Ingestion completed in {total_time:.2f}s")


if __name__ == "__main__":
    run_ingest()