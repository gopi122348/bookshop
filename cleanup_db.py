import os
db = '/tmp/db.sqlite3'
if os.path.exists(db):
    os.remove(db)
    print("Removed old db")
