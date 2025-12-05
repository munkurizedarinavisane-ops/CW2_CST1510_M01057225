import sqlite3
from pathlib import Path

# Ensure DATA folder exists
DATA_FOLDER = Path("../app/data")
DATA_FOLDER.mkdir(exist_ok=True)

# Path to your SQLite database file
DB_PATH = DATA_FOLDER / "intelligence_platform.db"

def connect_database():
    """Create and return a SQLite connection with dict-like rows."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # allows dict-like row access
    return conn

def execute_query(query, params=None, fetch=False, many=False):
    """Helper function to execute SQL queries safely."""
    conn = connect_database()
    cursor = conn.cursor()

    if params is None:
        params = ()

    try:
        if many:
            cursor.executemany(query, params)
        else:
            cursor.execute(query, params)

        if fetch:
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        conn.commit()
    except Exception as e:
        print("DB Error:", e)
        conn.rollback()
        raise e
    finally:
        conn.close()
