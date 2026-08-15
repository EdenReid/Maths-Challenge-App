import db
conn = db.get_connection()
row = conn.execute("SELECT * FROM problems").fetchall()
print(row)
conn.close()