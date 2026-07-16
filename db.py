import sqlite3

def get_connection():
    conn = sqlite3.connect("problems.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY,
            difficulty INTEGER,
            statement TEXT,
            answer TEXT
        )
    """)
    conn.commit()
    conn.close()
