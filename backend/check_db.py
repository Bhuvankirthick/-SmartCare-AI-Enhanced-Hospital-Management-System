import psycopg2
import sys
import os

# Add the current directory to sys.path so we can import from 'app'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config import settings

def check_db():
    print(f"Checking database at {settings.database_url.split('@')[-1]}...")
    try:
        conn = psycopg2.connect(settings.database_url)
        cursor = conn.cursor()
        
        # Check current database name
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()[0]
        print(f"Connected to database: {db_name}")
        
        # Check tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in 'public' schema.")
        else:
            print(f"Found {len(tables)} tables:")
            for t in tables:
                print(f" - {t[0]}")
                
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check_db()
