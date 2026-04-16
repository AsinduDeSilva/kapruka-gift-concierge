import uuid

from loguru import logger
from qdrant_client import QdrantClient
from typing import Any, Dict, List, Optional
from src.infrastructure.llm.embeddings import get_dense_embedder, get_sparse_embedder
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
    SparseVectorParams,
    Prefetch,
    FusionQuery
)

from src.infrastructure.config import (
    QDRANT_COLLECTION_NAME,
    EMBEDDING_DIM,
    PROJECT_ROOT
)


_qdrant_client: Optional[QdrantClient] = None

def get_qdrant_client() -> QdrantClient:

    global _qdrant_client
    if _qdrant_client is not None:
        return _qdrant_client

    _qdrant_client = QdrantClient(path=f"{PROJECT_ROOT}/data/qdrant_data")
    return _qdrant_client


def ensure_collection(
    collection_name: str = QDRANT_COLLECTION_NAME,
    vector_size: int = EMBEDDING_DIM,
    distance: Distance = Distance.COSINE,
) -> None:

    client = get_qdrant_client()

    if collection_exists():
        logger.info("Collection '{}' already exists — skipping creation.", collection_name)
        return

    client.create_collection(
        collection_name=collection_name,
        vectors_config={
            "dense": VectorParams(size=vector_size, distance=distance)
        },
        sparse_vectors_config={
            "sparse": SparseVectorParams()
        }
    )

    logger.info(
        "Created Qdrant collection '{}' (dim={}, distance={})",
        collection_name,
        vector_size,
        distance.name,
    )


def delete_collection(collection_name: str = QDRANT_COLLECTION_NAME) -> None:
    client = get_qdrant_client()
    client.delete_collection(collection_name)
    logger.info("Deleted Qdrant collection '{}'", collection_name)


def collection_info(collection_name: str = QDRANT_COLLECTION_NAME) -> Dict[str, Any]:
    client = get_qdrant_client()
    info = client.get_collection(collection_name)
    return {
        "name": collection_name,
        "points_count": info.points_count,
        "indexed_vectors_count": info.indexed_vectors_count,
        "vector_size": info.config.params.vectors.size,  # type: ignore[union-attr]
        "distance": info.config.params.vectors.distance.name,  # type: ignore[union-attr]
        "status": info.status.name,
    }


def upsert_products(
    products: List,
    dense_vectors: List[List[float]],
    sparse_vectors: List,
    collection_name: str = QDRANT_COLLECTION_NAME,
) -> None:

    client = get_qdrant_client()

    points = []

    for i, product in enumerate(products):
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector={
                    "dense": dense_vectors[i],
                    "sparse": sparse_vectors[i].as_object()
                },
                payload={
                    "title": product["title"],
                    "description": product["description"],
                    "price": product["price"],
                    "url": product["url"],
                    "availability": product["availability"],
                }
            )
        )

    client.upsert(collection_name=collection_name, points=points)


    logger.info("Upserted points into '{}'", collection_name)


def search_products(
    vector_query: str,
    keyword_query: str,
    top_k: int = 5,
    collection_name: str = QDRANT_COLLECTION_NAME,
) -> List[Dict[str, Any]]:

    dense_embedder = get_dense_embedder()
    dense_query = dense_embedder.embed_query(vector_query)

    sparse_embedder = get_sparse_embedder()
    sparse_query = list(sparse_embedder.embed([keyword_query]))[0].as_object()

    client = get_qdrant_client()

    response = client.query_points(
        collection_name=collection_name,
        prefetch=[
            Prefetch(query=dense_query, using="dense", limit=20),
            Prefetch(query=sparse_query, using="sparse", limit=20),
        ],
        query=FusionQuery(fusion="rrf"),
        limit=top_k
    )

    results = []
    for hit in response.points:
        payload = hit.payload
        result = {
            "title": payload.get("title"),
            "description": payload.get("description"),
            "price": payload.get("price"),
            "url": payload.get("url"),
            "availability": payload.get("availability")
        }

        results.append(result)

    return results


def count_points(collection_name: str = QDRANT_COLLECTION_NAME) -> int:
    client = get_qdrant_client()
    info = client.get_collection(collection_name)
    return info.points_count or 0


def collection_exists(collection_name: str = QDRANT_COLLECTION_NAME) -> bool:
    client = get_qdrant_client()
    existing = [c.name for c in client.get_collections().collections]
    return collection_name in existing



