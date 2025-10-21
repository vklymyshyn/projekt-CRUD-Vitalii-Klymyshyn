import sqlite3
from pathlib import Path

DB_PATH = "books.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # return rows like dict
    return conn

def run_migration():
    """Create table if not exists using SQL migration file."""
    migrations_dir = Path("migrations")
    migration_file = migrations_dir / "001_create_books_table.sql"

    with get_connection() as conn:
        with open(migration_file, "r", encoding="utf-8") as f:
            sql = f.read()
            conn.executescript(sql)
        conn.commit()
