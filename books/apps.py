"""App configuration for the books Django application."""
from django.apps import AppConfig


class BooksConfig(AppConfig):
    """Configuration class for the books app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'books'