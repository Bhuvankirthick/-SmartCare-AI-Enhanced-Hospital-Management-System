import psycopg2
from app.config import settings

def seed():
    try:
        conn = psycopg2.connect(settings.database_url)
        cursor = conn.cursor()
        
        with open('seed_data.sql', 'r') as f:
            sql = f.read()
            
        cursor.execute(sql)
        conn.commit()
        print("Database seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    seed()
