import sqlite3
conn = sqlite3.connect("problems.db")
conn.execute("ALTER TABLE problem_progress DROP COLUMN first_solved_at")
conn.commit()
conn.close()