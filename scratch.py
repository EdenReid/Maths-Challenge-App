import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

conn = psycopg.connect(os.environ["DATABASE_URL"])
print("Connected!")

cur = conn.execute("SELECT * FROM problems")
print(cur.fetchall())

conn.close()
