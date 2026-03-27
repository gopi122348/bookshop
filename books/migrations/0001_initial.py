from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunSQL(
            """CREATE TABLE IF NOT EXISTS "books_book" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "title" varchar(200) NOT NULL,
                "author" varchar(100) NOT NULL,
                "isbn" varchar(13) NOT NULL UNIQUE,
                "price" decimal NOT NULL,
                "stock" integer NOT NULL,
                "genre" varchar(20) NOT NULL,
                "description" text NOT NULL,
                "published_date" date NULL,
                "created_at" datetime NOT NULL,
                "updated_at" datetime NOT NULL
            )""",
            reverse_sql='DROP TABLE IF EXISTS "books_book"'
        ),
    ]
