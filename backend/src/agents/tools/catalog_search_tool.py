from src.db.qdrant_db_client import search_products

class CatalogSearchTool:
     def search(self, vector_query: str, keyword_query: str,):
        return search_products(
            vector_query.replace("gifts", "options"),
            keyword_query
        )
