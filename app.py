from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_session import Session
import threading

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Konfiguracja aplikacji
app.config["SECRET_KEY"] = "your1234"  # Upewnij się, że klucz jest unikalny i trudny do odgadnięcia
app.config["SESSION_TYPE"] = "filesystem"  # Przechowywanie sesji w plikach
app.config["PERMANENT_SESSION_LIFETIME"] = 3600  # Sesja wygasa po 1 godzinie
Session(app)

# Dane użytkowników i numerów
lock = threading.Lock()
current_numbers = {"Tomek": 1, "Mateusz": 1, "Dawid": 1}
users = {
    "Tomek": bcrypt.generate_password_hash("password1").decode("utf-8"),
    "Mateusz": bcrypt.generate_password_hash("password2").decode("utf-8"),
    "Dawid": bcrypt.generate_password_hash("password3").decode("utf-8"),
}

# Strona główna
@app.route("/")
def index():
    return render_template("index.html")

# Logowanie
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    # Obsługa logowania przez JSON
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    username = data.get("username")
    password = data.get("password")
    
    if username in users and bcrypt.check_password_hash(users[username], password):
        session["user"] = username
        return jsonify({"message": "Login successful"})
    
    return jsonify({"error": "Invalid credentials"}), 401

# Generowanie sygnatur
@app.route("/generate", methods=["GET"])
def generate():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    
    with lock:
        # Generowanie sygnatury
        signature = f"WK.B.{str(current_numbers[user]).zfill(4)}"
        current_numbers[user] += 1
    
    return render_template("generate.html", signature=signature)

if __name__ == "__main__":
    app.run(debug=True)