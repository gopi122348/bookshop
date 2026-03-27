import sqlite3, os
db = '/var/app/current/db.sqlite3'
if os.path.exists(db):
    conn = sqlite3.connect(db)
    conn.execute('DROP TABLE IF EXISTS books_order')
    conn.execute('DROP TABLE IF EXISTS books_orderitem')
    conn.commit()
    conn.close()
    print("Cleaned up bad tables")
