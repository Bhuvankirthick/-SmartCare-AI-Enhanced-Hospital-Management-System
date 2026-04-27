import psycopg2
try:
    conn = psycopg2.connect("postgresql://postgres:dbms@localhost:5432/hospital_db")
    print("Successfully connected to local hospital_db")
    conn.close()
except Exception as e:
    print(f"Failed to connect to local hospital_db: {e}")
    try:
        conn = psycopg2.connect("postgresql://postgres:dbms@localhost:5432/postgres")
        print("Successfully connected to local postgres db")
        conn.close()
    except Exception as e2:
        print(f"Failed to connect to local postgres db: {e2}")
