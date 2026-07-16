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
            source TEXT,
            difficulty INTEGER,
            statement TEXT UNIQUE,
            image_path TEXT,
            options TEXT,
            answer TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS problem_progress (
            problem_id INTEGER PRIMARY KEY,
            solved BOOLEAN DEFAULT 0,
            attempts INTEGER DEFAULT 0,
            first_solved_at TIMESTAMP,
            FOREIGN KEY(problem_id) REFERENCES problems(id)
        )
    """)
    conn.commit()
    conn.close()