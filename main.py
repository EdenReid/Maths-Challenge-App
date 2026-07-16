from db import init_db, get_connection

init_db()

conn = get_connection()
conn.execute(
    "INSERT INTO problems (difficulty, statement, answer) VALUES (?, ?, ?)",
    (1, "Solve x + 3 = 7", "4")
)
conn.commit()

rows = conn.execute("SELECT * FROM problems").fetchall()
for row in rows:
    print(dict(row))

conn.close()