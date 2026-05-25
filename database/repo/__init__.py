"""Repository layer — all DB queries live here.

Handlers should never write raw SQLAlchemy queries. Instead, call functions
from these modules. Each module groups operations on one entity.
"""

from database.repo import categories, products, purchases, settings, users

__all__ = ["users", "categories", "products", "purchases", "settings"]
