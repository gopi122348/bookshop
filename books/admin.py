# books/admin.py
# Register Book model with customised Django admin interface

from django.contrib import admin
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Custom admin view for managing books."""

    list_display = ['title', 'author', 'price', 'stock', 'genre', 'is_in_stock']
    list_filter = ['genre', 'created_at']
    search_fields = ['title', 'author', 'isbn']
    ordering = ['title']
    readonly_fields = ['created_at', 'updated_at']