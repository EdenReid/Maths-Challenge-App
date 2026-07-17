import json 
from db import get_connection

def import_questions(json_path):
    with open(json_path,"r") as f:
        questions = json.load(f)

    conn = get_connection()

    for q in questions:
        cursor = conn.execute("INSERT OR IGNORE INTO problems (source, difficulty, statement, image_path, options, answer) VALUES (?,?,?,?,?,?)", (q["source"], q["difficulty"], q["statement"], q["image_path"], json.dumps(q["options"]), q["answer"]))
        problem_id = cursor.lastrowid 
        conn.execute(
            "INSERT OR IGNORE INTO problem_progress (problem_id, solved, attempts) VALUES (?, 0, 0)", (problem_id,)
        )
    conn.commit()
    conn.close()
    
if __name__ == "__main__":
    import_questions("problems.json")