from src.db.qdrant_db_client import search_products


def search(query: str):
    return search_products(query)

