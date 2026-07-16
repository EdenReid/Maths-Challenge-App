from db import init_db, get_connection

init_db()

conn = get_connection()

rows = conn.execute("SELECT * FROM problems").fetchall()
for row in rows:
    print(dict(row))

conn.close()