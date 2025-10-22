CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    price REAL NOT NULL CHECK (price >= 0),
    published_year INTEGER NOT NULL CHECK (published_year >= 0),
    description TEXT DEFAULT ''
);
