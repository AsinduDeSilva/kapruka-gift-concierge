from src.db.qdrant_db_client import search_products
from src.infrastructure.observability import observe


class CatalogSearchTool:
     @observe(name="catalog_search")
     def search(self, vector_query: str, keyword_query: str,):
        return search_products(
            vector_query.replace("gifts", "options"),
            keyword_query
        )
