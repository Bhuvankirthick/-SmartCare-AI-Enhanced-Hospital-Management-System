import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Clean up URL like in database.py
db_url = db_url.replace("channel_binding=require", "")
db_url = db_url.replace("&&", "&").replace("?&", "?")

print(f"Testing connection to: {db_url.split('@')[-1]}")

try:
    conn = psycopg2.connect(db_url)
    print("SUCCESS: Connected to database!")
    cur = conn.cursor()
    cur.execute("SELECT version();")
    print(f"DB Version: {cur.fetchone()}")
    cur.close()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
