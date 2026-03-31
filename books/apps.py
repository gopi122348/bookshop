"""App configuration for the books app."""
from django.apps import AppConfig


class BooksConfig(AppConfig):
    """Configuration class for the books application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'books'