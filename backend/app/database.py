from psycopg2 import pool
import logging
from .config import settings

logger = logging.getLogger(__name__)

db_url = settings.database_url
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

connection_pool = None

def init_pool():
    global connection_pool
    db_url = settings.database_url
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    # Remove channel_binding if present as it can cause issues with some psycopg2 versions
    db_url = db_url.replace("channel_binding=require", "")
    db_url = db_url.replace("&&", "&").replace("?&", "?")
    
    print(f"DEBUG: Attempting to initialize pool with: {db_url.split('@')[-1]}")
    try:
        connection_pool = pool.ThreadedConnectionPool(1, 40, db_url)
        print(f"SUCCESS: Connected to PostgreSQL pool at {db_url.split('@')[-1]}")
    except Exception as e:
        print(f"CRITICAL: Error connecting to database pool: {e}")
        connection_pool = None

# Initial attempt
init_pool()

def get_db():
    global connection_pool
    if connection_pool is None:
        init_pool()
        if connection_pool is None:
            raise Exception("Database connection pool is not initialized. Check your DATABASE_URL.")

    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)
