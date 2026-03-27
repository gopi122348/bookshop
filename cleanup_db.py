import os, sqlite3

db = '/tmp/db.sqlite3'
try:
    if os.path.exists(db):
        os.remove(db)
        print("Removed old db")
except PermissionError:
    # Can't delete, so wipe all tables instead
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for (table,) in tables:
        conn.execute(f'DROP TABLE IF EXISTS "{table}"')
    conn.commit()
    conn.close()
    print("Wiped all tables in existing db")
