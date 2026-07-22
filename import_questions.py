import json 
import matplotlib.pyplot as plt
import matplotlib
from PIL import Image
matplotlib.use("Agg")
matplotlib.rcParams["text.usetex"] = True
matplotlib.rcParams["text.latex.preamble"] = r"\usepackage{amsmath}"
from db import get_connection
import os 
os.makedirs("images", exist_ok=True)

def import_questions(json_path):
    with open(json_path,"r") as f:
        questions = json.load(f)

    conn = get_connection()

    for q in questions:
        conn.execute("INSERT OR IGNORE INTO problems (source, difficulty, statement, image_path, options, answer) VALUES (?,?,?,?,?,?)", (q["source"], q["difficulty"], q["statement"], q["image_path"], json.dumps(q["options"]), q["answer"]))
        row = conn.execute("SELECT id FROM problems WHERE statement = ?", (q["statement"],)).fetchone()
        problem_id = row["id"]

        statement_image_path = os.path.join("images", f"q{problem_id}_statement.png")

        if not os.path.exists(statement_image_path):
            render_text_to_image(q["statement"], statement_image_path)
        conn.execute("""
            UPDATE problems
            SET statement_image = ?
            WHERE id = ?
        """, (statement_image_path, problem_id,)
        )

        options = q["options"]
        if options is not None:
            for opt in options:
                if opt["type"] == "text":
                    opt_image_path = os.path.join("images",f"q{problem_id}_opt{opt['id']}.png")
                    if not os.path.exists(opt_image_path):
                        render_option_image(opt["value"], opt_image_path, fontsize=28)
                    opt["image_path"] = opt_image_path
            conn.execute("UPDATE problems SET options = ? WHERE id = ?", (json.dumps(options), problem_id))
        
        conn.execute("""
            INSERT OR IGNORE INTO problem_progress (problem_id, solved, attempts) VALUES (?,0,0)
        """, (problem_id,))

    conn.commit()
    conn.close()

def render_text_to_image(text, output_path, fontsize=28, wrap_width_in=5):
    text = text.replace(r"\(","$").replace(r"\)","$")
    if "$" not in text:
        text = f"${text}$"
    wrapped = r"\parbox{" + f"{wrap_width_in}in" + "}{" + text + "}"
    fig = plt.figure(figsize=(wrap_width_in + 0.5, 3))
    fig.text(0, 1, wrapped, fontsize = fontsize, ha="left", va="top", wrap=True, color="white")
    plt.axis("off")
    plt.savefig(output_path, bbox_inches="tight", dpi=200, pad_inches=0.15, transparent=True)
    plt.close(fig)
    crop_to_content(output_path)

def render_option_image(text, output_path, fontsize=25):
    text = text.replace(r"\(","$").replace(r"\)","$")
    if "$" not in text:
        text = f"${text}$"
    fig = plt.figure(figsize=(6,1))
    fig.text(0, 0.5, text, fontsize = fontsize, ha="left", va="center", color="white")
    plt.axis("off")
    plt.savefig(output_path, bbox_inches="tight", dpi=200, pad_inches=0.15, transparent=True)
    plt.close(fig)

def crop_to_content(path):
    img = Image.open(path)
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        img.save(path)

if __name__ == "__main__":
    import_questions("problems.json")