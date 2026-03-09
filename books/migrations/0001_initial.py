import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('author', models.CharField(max_length=100)),
                ('isbn', models.CharField(help_text='13-digit ISBN, no dashes', max_length=13, unique=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=6, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('stock', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(9999)])),
                ('genre', models.CharField(choices=[('fiction', 'Fiction'), ('non_fiction', 'Non-Fiction'), ('science', 'Science'), ('history', 'History'), ('biography', 'Biography'), ('technology', 'Technology'), ('other', 'Other')], default='other', max_length=20)),
                ('description', models.TextField(blank=True)),
                ('published_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
    ]
