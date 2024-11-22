from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt
from flask_session import Session
import threading

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Konfiguracja aplikacji
app.config["SECRET_KEY"] = "your1234"  # Zmień na własny klucz
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

lock = threading.Lock()
current_numbers = {"Tomek": 1, "Mateusz": 1, "Dawid": 1}
prefix = "WK.B."
number_length = 4

users = {
    "user1": bcrypt.generate_password_hash("password1").decode("utf-8"),
    "user2": bcrypt.generate_password_hash("password2").decode("utf-8"),
    "user3": bcrypt.generate_password_hash("password3").decode("utf-8"),
}

def generate_signature(user):
    with lock:
        signature = f"{prefix}{str(current_numbers[user]).zfill(number_length)}"
        current_numbers[user] += 1
    return signature

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username in users and bcrypt.check_password_hash(users[username], password):
        session["user"] = username
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route("/generate", methods=["GET"])
def generate():
    user = session.get("user")
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    signature = generate_signature(user)
    return jsonify({"signature": signature})

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"message": "Logged out successfully"})

if __name__ == "__main__":
    app.run(debug=True)