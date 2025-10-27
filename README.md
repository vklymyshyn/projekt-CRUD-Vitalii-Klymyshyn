# Book CRUD Module

## Opis
Moduł CRUD dla encji `Book`:
- tabela w SQLite (`books.db`)
- API REST w Flask
- prosty frontend (HTML + JS) pozwalający listować, dodawać, edytować i usuwać książki.

## Jak uruchomić lokalnie

1. Wymagania:
   - Python 3.10+
   - pip
   - Visual Studio / VS Code (opcjonalnie)

2. Zainstaluj zależności:
   ```bash
   pip install -r requirements.txt
   ```

3. Uruchom backend + frontend:
   ```bash
   python app.py
   ```

4. Otwórz w przegladarce:
   http://127.0.0.1:5000/

5. Funkcje UI:
   - dodaj nową książkę
   - edytuj istniejącą
   - usuń książkę
   - zobacz listę książek

## Endpointy API

### GET /api/books
Zwraca listę wszystkich książek.

### GET /api/books/{id}
Zwraca jedną książkę.
- 404 jeśli nie istnieje.

### POST /api/books
Tworzy nową książkę.
Body (JSON):
```json
{
  "title": "string",
  "author": "string",
  "price": 19.99,
  "published_year": 2020,
  "description": "optional text"
}
```
- 400 jeśli walidacja nie przeszła.
- 201 jeśli OK.

### PUT /api/books/{id}
Aktualizuje książkę o danym `id`.
Body jak wyżej.
- 404 jeśli nie istnieje.
- 400 jeśli walidacja nie przeszła.

### DELETE /api/books/{id}
Usuwa książkę.
- 404 jeśli nie istnieje.

## Migracja SQL
Plik `migrations/001_create_books_table.sql` tworzy tabelę `books` w czystej bazie SQLite.
Skrypt `app.py` automatycznie odpala migrację przy starcie.
