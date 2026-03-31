from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('books', '0002_order_orderitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(default='Home', help_text='A short label, e.g. Home or Work', max_length=50)),
                ('full_name', models.CharField(max_length=100)),
                ('address_line1', models.CharField(max_length=200)),
                ('address_line2', models.CharField(blank=True, max_length=200)),
                ('city', models.CharField(max_length=100)),
                ('postcode', models.CharField(max_length=20)),
                ('country', models.CharField(default='Ireland', max_length=100)),
                ('is_default', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'addresses',
                'ordering': ['-is_default', '-created_at'],
            },
        ),
    ]