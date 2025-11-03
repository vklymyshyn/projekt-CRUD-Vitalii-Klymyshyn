import os
import datetime as dt
from functools import wraps
from pathlib import Path
import jwt
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from db import run_migration
import models
import models_user

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")

run_migration()

def issue_token(user_id: int, email: str, expires_minutes: int = 60 * 24):
    now = dt.datetime.utcnow()
    payload = {
        "sub": str(user_id),
        "email": email,
        "iat": now,
        "exp": now + dt.timedelta(minutes=expires_minutes),
    }
    token = jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")
    return token if isinstance(token, str) else token.decode("utf-8")

def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "Missing Authorization"}), 401
        token = auth.split(" ", 1)[1].strip()
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = int(payload.get("sub"))
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except Exception:
            return jsonify({"error": "Invalid token"}), 401
        user = models_user.get_user_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 401
        request.user = {"id": user["id"], "email": user["email"]}
        return fn(*args, **kwargs)
    return wrapper

def validate_book_payload(payload, require_all=True):
    if not isinstance(payload, dict):
        return False, "JSON body required"
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
        if "title" in payload and not payload["title"]:
            return False, "title cannot be empty"
        if "author" in payload and not payload["author"]:
            return False, "author cannot be empty"
    except (ValueError, TypeError):
        return False, "Invalid field types"
    return True, None

@app.route("/api/auth/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or "@" not in email:
        return jsonify({"error": "Valid email required"}), 400
    if not password or len(password) < 6:
        return jsonify({"error": "Password too short"}), 400
    if models_user.find_user_by_email(email):
        return jsonify({"error": "Email already registered"}), 409
    pwd_hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)
    user = models_user.create_user(email, pwd_hash)
    token = issue_token(user["id"], user["email"])
    return jsonify({"token": token, "user": {"id": user["id"], "email": user["email"]}}), 201

@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    user = models_user.find_user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid credentials"}), 401
    token = issue_token(user["id"], user["email"])
    return jsonify({"token": token, "user": {"id": user["id"], "email": user["email"]}}), 200

@app.route("/api/auth/me", methods=["GET"])
@auth_required
def api_me():
    return jsonify({"user": request.user}), 200

@app.route("/api/books", methods=["GET"])
@auth_required
def api_list_books():
    data = models.list_books()
    return jsonify(data), 200

@app.route("/api/books/<int:book_id>", methods=["GET"])
@auth_required
def api_get_book(book_id):
    b = models.get_book(book_id)
    if not b:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(b), 200

@app.route("/api/books", methods=["POST"])
@auth_required
def api_create_book():
    payload = request.get_json(silent=True) or {}
    ok, err = validate_book_payload(payload, require_all=True)
    if not ok:
        return jsonify({"error": err}), 400
    new_book = models.create_book(payload)
    return jsonify(new_book), 201

@app.route("/api/books/<int:book_id>", methods=["PUT", "PATCH"])
@auth_required
def api_update_book(book_id):
    payload = request.get_json(silent=True) or {}
    ok, err = validate_book_payload(payload, require_all=False)
    if not ok:
        return jsonify({"error": err}), 400
    updated = models.update_book(book_id, payload)
    if updated == 0:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"status": "updated"}), 200

@app.route("/api/books/<int:book_id>", methods=["DELETE"])
@auth_required
def api_delete_book(book_id):
    deleted = models.delete_book(book_id)
    if deleted == 0:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"status": "deleted"}), 200

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    app.run(debug=True)
