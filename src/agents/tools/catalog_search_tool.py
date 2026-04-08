from src.db.qdrant_db_client import search_products

class CatalogSearchTool:
    def search(self, query: str):
        return search_products(query)

