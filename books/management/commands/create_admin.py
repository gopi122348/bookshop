from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from books.models import Book

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        U = get_user_model()
        if not U.objects.filter(username='admin').exists():
            U.objects.create_superuser('admin', 'admin@example.com', 'Admin1234!')
            self.stdout.write('Superuser created.')

        if Book.objects.count() == 0:
            Book.objects.create(title='The Midnight Library', author='Matt Haig', price=12.99, stock=10, genre='FIC', isbn='9780525559474')
            Book.objects.create(title='Atomic Habits', author='James Clear', price=14.99, stock=15, genre='NON', isbn='9780735211292')
            Book.objects.create(title='1984', author='George Orwell', price=9.99, stock=20, genre='FIC', isbn='9780451524935')
            self.stdout.write('Sample books created.')
