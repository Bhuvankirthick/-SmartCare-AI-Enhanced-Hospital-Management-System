import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import logging
from .config import settings

logger = logging.getLogger(__name__)

# Create a connection pool to manage concurrent execution safely
# We use ThreadedConnectionPool for thread safety in FastAPI
try:
    connection_pool = pool.ThreadedConnectionPool(
        1, 40,
        settings.database_url
    )
    if connection_pool:
        print(f"Connected to PostgreSQL at {settings.database_url.split('@')[-1]}")
except Exception as e:
    print("Error connecting to database:", e)
    connection_pool = None


def get_db():
    if connection_pool is None:
        raise Exception("Database connection pool is not initialized. Check your DATABASE_URL.")
    
    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)
