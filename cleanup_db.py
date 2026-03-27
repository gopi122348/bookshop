import os, sqlite3

db = '/tmp/db.sqlite3'
try:
    if os.path.exists(db):
        os.remove(db)
except:
    pass

try:
    conn = sqlite3.connect(db)
    for table in ['books_book','books_order','books_orderitem','django_migrations']:
        conn.execute(f'DROP TABLE IF EXISTS "{table}"')
    conn.commit()
    conn.close()
except:
    pass

print("DB cleanup done")
