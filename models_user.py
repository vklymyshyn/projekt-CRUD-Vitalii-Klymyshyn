from typing import Optional, Dict
from db import get_connection

def find_user_by_email(email: str) -> Optional[Dict]:
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM users WHERE email = ?;", (email,))
        row = cur.fetchone()
        return dict(row) if row else None

def create_user(email: str, password_hash: str) -> Dict:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO users(email, password_hash) VALUES(?, ?);",
            (email, password_hash),
        )
        conn.commit()
        user_id = cur.lastrowid
        cur = conn.execute("SELECT * FROM users WHERE id = ?;", (user_id,))
        row = cur.fetchone()
        return dict(row)

def get_user_by_id(user_id: int) -> Optional[Dict]:
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM users WHERE id = ?;", (user_id,))
        row = cur.fetchone()
        return dict(row) if row else None
