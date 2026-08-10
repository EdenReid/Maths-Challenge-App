import sqlite3
import db 

conn = db.get_connection()

conn.execute("UPDATE problems SET source = 'TMUA Paper 1' WHERE source = 'TMUA'")
conn.commit()
conn.close()