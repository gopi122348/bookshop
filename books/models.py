# Book database model with validation constraints
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Book(models.Model):
    """Represents a book in the online bookshop with full CRUD support."""

    GENRE_CHOICES = [
        ('fiction', 'Fiction'),
        ('non_fiction', 'Non-Fiction'),
        ('science', 'Science'),
        ('history', 'History'),
        ('biography', 'Biography'),
        ('technology', 'Technology'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)

    isbn = models.CharField(
        max_length=13,
        unique=True,
        help_text="13-digit ISBN, no dashes"
    )

    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(9999)]
    )

    genre = models.CharField(
        max_length=20,
        choices=GENRE_CHOICES,
        default='other'
    )

    description = models.TextField(blank=True)

    published_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        """Return readable representation of the book."""
        return f"{self.title} by {self.author}"

    def is_in_stock(self):
        """Return True if at least one copy is available."""
        return self.stock > 0
    class Order(models.Model):
    """A customer order, always linked to a registered user."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    total_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.pk} — {self.customer_name}'


class OrderItem(models.Model):
    """One line in an order: one book type + quantity."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField(default=1)

    price = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )

    def __str__(self):
        return f'{self.quantity}x {self.book.title}'

    def subtotal(self):
        """Price multiplied by quantity for this line."""
        return self.price * self.quantity