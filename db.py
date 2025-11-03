import sqlite3
from pathlib import Path

DB_PATH = "books.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # return rows like dict
    return conn

def run_migration():
    """Execute all SQL files in migrations/ sorted by name."""
    migrations_dir = Path("migrations")
    sql_files = sorted(p for p in migrations_dir.glob("*.sql"))
    if not sql_files:
        return

    with get_connection() as conn:
        for f in sql_files:
            with open(f, "r", encoding="utf-8") as fh:
                sql = fh.read()
                conn.executescript(sql)
        conn.commit()
