"""
Services - Lógica de negócio e integrações externas.
"""

from app.services import scraper, vector_db, document_generator

__all__ = ["scraper", "vector_db", "document_generator"]