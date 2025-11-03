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
            INSERT INTO books(title, author, price, published_year, description)
            VALUES(?, ?, ?, ?, ?);
            """,
            (
                data["title"],
                data["author"],
                float(data["price"]),
                int(data["published_year"]),
                data.get("description", ""),
            ),
        )
        conn.commit()
        new_id = cur.lastrowid
        cur = conn.execute("SELECT * FROM books WHERE id = ?;", (new_id,))
        return dict(cur.fetchone())

def update_book(book_id: int, data: dict):
    fields = []
    values = []
    for key in ("title", "author", "price", "published_year", "description"):
        if key in data:
            fields.append(f"{key} = ?")
            if key == "price":
                values.append(float(data[key]))
            elif key == "published_year":
                values.append(int(data[key]))
            else:
                values.append(data[key])
    if not fields:
        return 0
    values.append(book_id)
    sql = f"UPDATE books SET {', '.join(fields)} WHERE id = ?;"
    with get_connection() as conn:
        cur = conn.execute(sql, tuple(values))
        conn.commit()
        return cur.rowcount

def delete_book(book_id: int):
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM books WHERE id = ?;", (book_id,))
        conn.commit()
        return cur.rowcount
