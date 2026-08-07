import sqlite3
import random

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
            answer TEXT,
            statement_image TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS problem_progress (
            problem_id INTEGER PRIMARY KEY,
            solved BOOLEAN DEFAULT 0,
            attempts INTEGER DEFAULT 0,
            first_attempt_correct BOOLEAN DEFAULT NULL,
            FOREIGN KEY(problem_id) REFERENCES problems(id)
        )
    """)
    conn.commit()
    conn.close()

def get_random_unsolved_problem():
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM problems, problem_progress WHERE problem_progress.problem_id = problems.id AND problem_progress.solved = 0
    """).fetchall()
    conn.close()
    if not rows:
        return None
    return dict(random.choice(rows))

def check_solution(problem_id, student_answer):
    conn = get_connection()
    conn.execute("""
       UPDATE problem_progress
       SET attempts = attempts + 1
       WHERE problem_id = ?          
    """,(problem_id,))
    answer = conn.execute("SELECT answer FROM problems WHERE id = ?", (problem_id,)).fetchone()
    answer = answer["answer"]
    attempts = conn.execute("SELECT attempts FROM problem_progress WHERE problem_id = ?",(problem_id,)).fetchone()
    attempts = attempts["attempts"]
    if answer == student_answer:
        conn.execute("""
            UPDATE problem_progress
            SET solved = True
            WHERE problem_id = ?
        """,(problem_id,))
        if attempts == 1:
            conn.execute("""
                UPDATE problem_progress
                SET first_attempt_correct = True
                WHERE problem_id = ?
            """,(problem_id,))
    else:
        if attempts == 1:
            conn.execute("""
                UPDATE problem_progress
                SET first_attempt_correct = False
                WHERE problem_id = ?
            """,(problem_id,))
    conn.commit()
    conn.close()
    return answer == student_answer 

def get_all_probs_with_progress(source=None, difficulty=None, solved=None):
    conn = get_connection()
    query = """
        SELECT problems.*, problem_progress.solved, problem_progress.attempts 
        FROM problems, problem_progress
        WHERE problems.id = problem_progress.problem_id
    """
    params = []
    if source is not None:
        query += "AND problems.source = ?"
        params.append(source)
    if difficulty is not None:
        query += "AND problems.difficulty = ?"
        params.append(difficulty)
    if solved is not None:
        query += "AND problem_progress.solved = ?"
        params.append(solved)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_total_problems():
    conn = get_connection()
    probs = conn.execute("SELECT * FROM problems").fetchall()
    conn.close()
    return len(probs)

def get_total_solved():
    conn = get_connection()
    probs = conn.execute("""
        SELECT * FROM problem_progress WHERE solved = 1
    """).fetchall()
    conn.close()
    return len(probs)

def get_first_attempt_correct():
    conn = get_connection()
    probs = conn.execute("SELECT * FROM problem_progress WHERE first_attempt_correct = 1").fetchall()
    conn.close()
    return len(probs)

def get_total_xp():
    conn = get_connection()
    row = conn.execute("""
        SELECT SUM(problems.difficulty) as total_xp
        FROM problems, problem_progress
        WHERE problems.id = problem_progress.problem_id AND problem_progress.first_attempt_correct = 1
    """).fetchone()
    return row["total_xp"] if row["total_xp"] is not None else 0

