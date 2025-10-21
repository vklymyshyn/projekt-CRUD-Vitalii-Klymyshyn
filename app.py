from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from db import run_migration
import models

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

# inicjalizacja bazy danych
run_migration()

# prosta wersja endpointów bez walidacji i obsługi błędów

@app.route("/api/books", methods=["GET"])
def get_books():
    data = models.list_books()
    return jsonify(data)

@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = models.get_book(book_id)
    return jsonify(book)

@app.route("/api/books", methods=["POST"])
def create_book():
    payload = request.get_json()
    new_id = models.create_book(payload)
    book = models.get_book(new_id)
    return jsonify(book)

@app.route("/api/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    payload = request.get_json()
    models.update_book(book_id, payload)
    book = models.get_book(book_id)
    return jsonify(book)

@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    models.delete_book(book_id)
    return jsonify({"status": "deleted"})

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    app.run(debug=True)
