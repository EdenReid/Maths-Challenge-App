import sqlite3
conn = sqlite3.connect("problems.db")
conn.execute("ALTER TABLE problem_progress ADD COLUMN first_attempt_correct BOOLEAN DEFAULT NULL")
conn.commit()
conn.close()