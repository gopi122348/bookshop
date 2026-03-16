"""
books/tests.py
Unit tests for Book model and views — runs automatically in GitHub Actions CI.
"""
from django.test import TestCase, Client
from django.urls import reverse
from .models import Book


class BookModelTest(TestCase):
    """Unit tests for the Book model."""

    def setUp(self):
        """Create a sample book used in all model tests."""
        self.book = Book.objects.create(
            title='Test Book', author='Test Author',
            isbn='9780000000001', price=9.99,
            stock=10, genre='fiction'
        )

    def test_book_creation(self):
        """Book is saved with correct attributes."""
        self.assertEqual(self.book.title, 'Test Book')
        self.assertEqual(self.book.author, 'Test Author')

    def test_book_str(self):
        """__str__ returns title and author."""
        self.assertEqual(str(self.book), 'Test Book by Test Author')

    def test_is_in_stock_true(self):
        """is_in_stock returns True when stock > 0."""
        self.assertTrue(self.book.is_in_stock())

    def test_is_in_stock_false(self):
        """is_in_stock returns False when stock is 0."""
        self.book.stock = 0
        self.assertFalse(self.book.is_in_stock())


class BookViewTest(TestCase):
    """Integration tests for CRUD views."""

    def setUp(self):
        """Create client and test book."""
        self.client = Client()
        self.book = Book.objects.create(
            title='View Test Book', author='View Author',
            isbn='9780000000002', price=14.99,
            stock=5, genre='science'
        )

    def test_book_list_returns_200(self):
        """Book list page loads successfully."""
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'View Test Book')

    def test_book_detail_returns_200(self):
        """Book detail page loads for existing book."""
        response = self.client.get(
            reverse('book_detail', args=[self.book.pk]))
        self.assertEqual(response.status_code, 200)

    def test_book_create_page_loads(self):
        """Add book form page loads."""
        response = self.client.get(reverse('book_create'))
        self.assertEqual(response.status_code, 200)

    def test_book_create_valid_data(self):
        """Valid POST to book_create redirects to list."""
        data = {
            'title': 'New Book', 'author': 'New Author',
            'isbn': '9780000000099', 'price': '12.99',
            'stock': '3', 'genre': 'history', 'description': ''
        }
        response = self.client.post(reverse('book_create'), data)
        self.assertEqual(response.status_code, 302)

    def test_book_create_invalid_isbn(self):
        """Short ISBN stays on form with error message."""
        data = {
            'title': 'Bad Book', 'author': 'Bad Author',
            'isbn': '123', 'price': '10.00',
            'stock': '1', 'genre': 'other'
        }
        response = self.client.post(reverse('book_create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ISBN must be exactly 13 digits')

    def test_book_delete(self):
        """POST to book_delete removes book from database."""
        response = self.client.post(
            reverse('book_delete', args=[self.book.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Book.objects.filter(pk=self.book.pk).exists())