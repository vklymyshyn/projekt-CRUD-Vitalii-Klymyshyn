from db import get_connection

def list_books():
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM books ORDER BY id ASC;")
        rows = cur.fetchall()
        return [dict(r) for r in rows]


def get_book(book_id: int):
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM books WHERE id = ?;", (book_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def create_book(data: dict):
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO books (title, author, price, published_year, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                data["title"],
                data["author"],
                data["price"],
                data["published_year"],
                data.get("description", ""),
            ),
        )
        conn.commit()
        return cur.lastrowid


def update_book(book_id: int, data: dict):
    with get_connection() as conn:
        cur = conn.execute(
            """
            UPDATE books
            SET title = ?, author = ?, price = ?, published_year = ?, description = ?
            WHERE id = ?
            """,
            (
                data["title"],
                data["author"],
                data["price"],
                data["published_year"],
                data.get("description", ""),
                book_id,
            ),
        )
        conn.commit()
        return cur.rowcount  # 0 = not found, 1 = updated


def delete_book(book_id: int):
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM books WHERE id = ?;", (book_id,))
        conn.commit()
        return cur.rowcount

