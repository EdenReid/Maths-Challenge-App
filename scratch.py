import sqlite3
conn = sqlite3.connect("problems.db")
conn.execute("ALTER TABLE problems DROP COLUMN statement_image")
conn.execute("ALTER TABLE problems ADD statement_image TEXT")
conn.commit()
conn.close()