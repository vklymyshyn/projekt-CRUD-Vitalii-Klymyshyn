from db import get_connection

def list_books():
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM books ORDER BY id ASC;")
        rows = cur.fetchall()
        return [dict(r) for r in rows]


def get_book(book_id):
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM books WHERE id = ?;", (book_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def create_book(data):
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO books (title, author, price, published_year) VALUES (?, ?, ?, ?);",
            (data["title"], data["author"], data["price"], data["published_year"]),
        )
        conn.commit()
        return cur.lastrowid
