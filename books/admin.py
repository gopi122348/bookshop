# books/admin.py
# Register Book, Order, and OrderItem models with customised Django admin interface

from django.contrib import admin
from .models import Book, Order, OrderItem


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Custom admin view for managing books."""
    list_display = ['title', 'author', 'price', 'stock', 'genre', 'is_in_stock']
    list_filter = ['genre', 'created_at']
    search_fields = ['title', 'author', 'isbn']
    ordering = ['title']
    readonly_fields = ['created_at', 'updated_at']


class OrderItemInline(admin.TabularInline):
    """Show order items inline within the order."""
    model = OrderItem
    extra = 0
    readonly_fields = ['book', 'quantity', 'price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Custom admin view for managing orders."""
    list_display = [
        'pk',
        'user',
        'customer_name',
        'customer_email',
        'total_price',
        'status',
        'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = [
        'customer_name',
        'customer_email',
        'user__username'
    ]
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'total_price', 'user']
    inlines = [OrderItemInline]