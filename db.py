import random
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

def get_connection():
    conn = psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row)
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS problems (
            id SERIAL PRIMARY KEY,
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
            problem_id INTEGER,
            user_id TEXT,
            solved BOOLEAN DEFAULT FALSE,
            attempts INTEGER DEFAULT 0,
            first_attempt_correct BOOLEAN,
            PRIMARY KEY (problem_id, user_id),
            FOREIGN KEY(problem_id) REFERENCES problems(id)
        )
    """)
    conn.commit()
    conn.close()

def get_random_unsolved_problem(user_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT problems.* FROM problems
        LEFT JOIN problem_progress
            ON problems.id = problem_progress.problem_id AND problem_progress.user_id = %s
        WHERE problem_progress.solved IS NULL OR problem_progress.solved = FALSE
    """, (user_id,)).fetchall()
    conn.close()
    if not rows:
        return None
    return dict(random.choice(rows))

def check_solution(problem_id, user_id, student_answer):
    conn = get_connection()

    conn.execute("""
        INSERT INTO problem_progress (problem_id, user_id) VALUES (%s,%s)
        ON CONFLICT (problem_id, user_id) DO NOTHING
    """, (problem_id, user_id)
    )

    conn.execute("""
       UPDATE problem_progress
       SET attempts = attempts + 1
       WHERE problem_id = %s AND user_id = %s
    """,(problem_id, user_id))

    answer = conn.execute("SELECT answer FROM problems WHERE id = %s", (problem_id,)).fetchone()
    answer = answer["answer"]
    attempts = conn.execute("SELECT attempts FROM problem_progress WHERE problem_id = %s AND user_id = %s",(problem_id, user_id)).fetchone()
    attempts = attempts["attempts"]

    if answer == student_answer:
        conn.execute("""
            UPDATE problem_progress
            SET solved = TRUE
            WHERE problem_id = %s AND user_id = %s
        """,(problem_id, user_id))
        if attempts == 1:
            conn.execute("""
                UPDATE problem_progress
                SET first_attempt_correct = TRUE
                WHERE problem_id = %s AND user_id = %s
            """,(problem_id, user_id))
    else:
        if attempts == 1:
            conn.execute("""
                UPDATE problem_progress
                SET first_attempt_correct = FALSE
                WHERE problem_id = %s AND user_id = %s
            """,(problem_id, user_id))

    conn.commit()
    conn.close()

    return answer == student_answer

def is_first_attempt(problem_id, user_id):
    conn = get_connection()
    row = conn.execute("SELECT attempts FROM problem_progress WHERE problem_id = %s AND user_id = %s", (problem_id, user_id)).fetchone()
    conn.close()
    return row["attempts"] == 1

def get_all_probs_with_progress(user_id, source=None, difficulty=None, solved=None):
    conn = get_connection()
    query = """
        SELECT problems.*, problem_progress.solved, problem_progress.attempts
        FROM problems
        LEFT JOIN problem_progress
            ON problems.id = problem_progress.problem_id AND problem_progress.user_id = %s
        WHERE 1=1
    """
    params = [user_id]
    if source is not None:
        query += "AND problems.source = %s "
        params.append(source)
    if difficulty is not None:
        query += "AND problems.difficulty = %s "
        params.append(difficulty)
    if solved is not None:
        solved_bool = bool(int(solved))
        if not solved_bool:
            query += "AND (problem_progress.solved = %s OR problem_progress.solved IS NULL) "
        else:
            query += "AND problem_progress.solved = %s"
        params.append(solved_bool)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_total_problems():
    conn = get_connection()
    probs = conn.execute("SELECT * FROM problems").fetchall()
    conn.close()
    return len(probs)

def get_total_solved(user_id):
    conn = get_connection()
    probs = conn.execute("""
        SELECT * FROM problem_progress WHERE solved = TRUE AND user_id = %s
    """, (user_id,)).fetchall()
    conn.close()
    return len(probs)

def num_first_attempt_correct(user_id):
    conn = get_connection()
    probs = conn.execute("SELECT * FROM problem_progress WHERE first_attempt_correct = TRUE AND user_id = %s", (user_id,)).fetchall()
    conn.close()
    return len(probs)

def get_total_xp(user_id):
    conn = get_connection()
    row = conn.execute("""
        SELECT SUM(problems.difficulty) as total_xp
        FROM problems, problem_progress
        WHERE problems.id = problem_progress.problem_id AND problem_progress.user_id = %s AND problem_progress.first_attempt_correct = TRUE
    """, (user_id,)).fetchone()
    conn.close()
    return row["total_xp"] if row["total_xp"] is not None else 0

