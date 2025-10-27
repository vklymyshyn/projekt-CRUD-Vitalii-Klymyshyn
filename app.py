from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
from db import run_migration
import models

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

# init DB / migration
run_migration()

def validate_book_payload(payload, require_all=True):
    """
    require_all=True for POST/PUT.
    Checks required fields and types.
    Returns (is_valid: bool, message: str)
    """
    required_fields = ["title", "author", "price", "published_year"]

    if require_all:
        for f in required_fields:
            if f not in payload:
                return False, f"Missing field: {f}"

    try:
        if "price" in payload:
            payload["price"] = float(payload["price"])
            if payload["price"] < 0:
                return False, "price must be >= 0"
        if "published_year" in payload:
            payload["published_year"] = int(payload["published_year"])
            if payload["published_year"] < 0:
                return False, "published_year must be >= 0"
    except ValueError:
        return False, "price must be number, published_year must be integer"

    for text_f in ["title", "author"]:
        if text_f in payload and (not isinstance(payload[text_f], str) or payload[text_f].strip() == ""):
            return False, f"{text_f} must be non-empty string"

    return True, "ok"

@app.route("/api/books", methods=["GET"])
def api_list_books():
    data = models.list_books()
    return jsonify(data), 200

@app.route("/api/books/<int:book_id>", methods=["GET"])
def api_get_book(book_id):
    book = models.get_book(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book), 200

@app.route("/api/books", methods=["POST"])
def api_create_book():
    if not request.is_json:
        return jsonify({"error": "Expected JSON"}), 400
    payload = request.get_json()

    ok, msg = validate_book_payload(payload, require_all=True)
    if not ok:
        return jsonify({"error": msg}), 400

    new_id = models.create_book(payload)
    new_book = models.get_book(new_id)
    return jsonify(new_book), 201

@app.route("/api/books/<int:book_id>", methods=["PUT"])
def api_update_book(book_id):
    if not request.is_json:
        return jsonify({"error": "Expected JSON"}), 400
    payload = request.get_json()

    ok, msg = validate_book_payload(payload, require_all=True)
    if not ok:
        return jsonify({"error": msg}), 400

    updated = models.update_book(book_id, payload)
    if updated == 0:
        return jsonify({"error": "Book not found"}), 404

    book_after = models.get_book(book_id)
    return jsonify(book_after), 200

@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def api_delete_book(book_id):
    deleted = models.delete_book(book_id)
    if deleted == 0:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"status": "deleted"}), 200

# serve frontend
@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    app.run(debug=True)
