"""Database models for books, addresses, and orders."""
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Book(models.Model):
    """A book available in the bookshop."""

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

    published_date = models.DateField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        default=timezone.now
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        """Meta options for the Book model."""

        ordering = ['title']

    def __str__(self):
        """Return a human-readable string representation of the book."""
        return f"{self.title} by {self.author}"

    def is_in_stock(self):
        """Return True if at least one copy is available."""
        return self.stock > 0


class Address(models.Model):
    """A saved delivery address belonging to a registered user."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses'
    )

    label = models.CharField(
        max_length=50,
        default='Home',
        help_text="A short label, e.g. Home or Work"
    )

    full_name = models.CharField(max_length=100)
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Ireland')

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        """Meta options for the Address model."""

        ordering = ['-is_default', '-created_at']
        verbose_name_plural = 'addresses'

    def __str__(self):
        """Return a short label and first line for this address."""
        return f"{self.label} – {self.address_line1}, {self.city}"

    def as_text(self):
        """Return the full address as a plain-text string."""
        parts = [self.full_name, self.address_line1]
        if self.address_line2:
            parts.append(self.address_line2)
        parts += [self.city, self.postcode, self.country]
        return ', '.join(parts)


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

    created_at = models.DateTimeField(
        default=timezone.now
    )

    class Meta:
        """Meta options for the Order model."""

        ordering = ['-created_at']

    def __str__(self):
        """Return a human-readable representation of the order."""
        return f"Order #{self.pk} - {self.customer_name}"


class OrderItem(models.Model):
    """A single book line item within an order."""

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
        """Return quantity and book title for this line item."""
        return f"{self.quantity}x {self.book.title}"

    def subtotal(self):
        """Return the total price for this line item."""
        return self.price * self.quantity