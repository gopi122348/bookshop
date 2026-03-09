from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Book, Order

class AuthTest(TestCase):
    """Tests for registration and login."""

    def test_register_page_loads(self):
        """Register page returns 200."""
        resp = self.client.get(reverse('register'))
        self.assertEqual(resp.status_code, 200)

    def test_register_creates_user(self):
        """Valid POST creates user and redirects."""
        resp = self.client.post(
            reverse('register'),
            {
                'username': 'testbuyer',
                'password1': 'StrongPass123!',
                'password2': 'StrongPass123!',
            }
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(User.objects.filter(username='testbuyer').exists())

    def test_login_page_loads(self):
        """Login page returns 200."""
        resp = self.client.get(reverse('login'))
        self.assertEqual(resp.status_code, 200)

    def test_cart_requires_login(self):
        """Unauthenticated user is redirected away from the cart."""
        resp = self.client.get(reverse('cart_view'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/accounts/login/', resp['Location'])


class PurchaseFlowTest(TestCase):
    """Full cart → checkout → order history flow."""

    def setUp(self):
        """Create a user and a book."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='buyer',
            password='TestPass99!'
        )
        self.book = Book.objects.create(
            title='Buy Me',
            author='Author A',
            isbn='9780000000003',
            price=9.99,
            stock=5,
            genre='fiction'
        )
        self.client.login(username='buyer', password='TestPass99!')

    def test_add_to_cart(self):
        """POST to cart_add adds book to session."""
        self.client.post(reverse('cart_add', args=[self.book.pk]))
        cart = self.client.session.get('cart', {})
        self.assertIn(str(self.book.pk), cart)

    def test_remove_from_cart(self):
        """POST to cart_remove empties cart."""
        self.client.post(reverse('cart_add', args=[self.book.pk]))
        self.client.post(reverse('cart_remove', args=[self.book.pk]))
        cart = self.client.session.get('cart', {})
        self.assertNotIn(str(self.book.pk), cart)

    def test_checkout_creates_order(self):
        """Valid checkout creates Order and decreases stock."""
        self.client.post(reverse('cart_add', args=[self.book.pk]))
        self.client.post(
            reverse('checkout'),
            {
                'customer_name': 'Jane Doe',
                'customer_email': 'jane@example.com',
                'customer_phone': '',
                'address': '1 Main St, Dublin',
            }
        )
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.user, self.user)
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock, 4)

    def test_order_history_visible(self):
        """Order history page shows completed orders."""
        Order.objects.create(
            user=self.user,
            customer_name='Jane',
            customer_email='j@e.com',
            address='1 St',
            total_price=9.99
        )
        resp = self.client.get(reverse('order_history'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Jane')

    def test_order_history_only_own_orders(self):
        """A user cannot see another user's orders."""
        other = User.objects.create_user(
            username='other',
            password='OtherPass99!'
        )
        Order.objects.create(
            user=other,
            customer_name='Other Person',
            customer_email='o@o.com',
            address='2 St',
            total_price=5.00
        )
        resp = self.client.get(reverse('order_history'))
        self.assertNotContains(resp, 'Other Person')

    def test_checkout_invalid_form(self):
        """Empty name keeps user on checkout page."""
        self.client.post(reverse('cart_add', args=[self.book.pk]))
        resp = self.client.post(
            reverse('checkout'),
            {
                'customer_name': '',
                'customer_email': 'jane@example.com',
                'address': '1 St',
            }
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)