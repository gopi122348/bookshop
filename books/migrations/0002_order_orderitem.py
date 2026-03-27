from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS books_order (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, created_at datetime NOT NULL, status varchar(20) NOT NULL, user_id integer NOT NULL REFERENCES auth_user(id))",
            reverse_sql="DROP TABLE IF EXISTS books_order"
        ),
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS books_orderitem (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, quantity integer NOT NULL, book_id integer NOT NULL REFERENCES books_book(id), order_id integer NOT NULL REFERENCES books_order(id))",
            reverse_sql="DROP TABLE IF EXISTS books_orderitem"
        ),
    ]
