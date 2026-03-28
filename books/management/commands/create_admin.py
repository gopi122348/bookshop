from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        U = get_user_model()
        if not U.objects.filter(username='admin').exists():
            U.objects.create_superuser('admin', 'admin@example.com', 'Admin1234!')
            self.stdout.write('Superuser created.')
        else:
            self.stdout.write('Superuser already exists.')
