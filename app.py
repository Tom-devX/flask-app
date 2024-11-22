from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Konfiguracja aplikacji
app.config["SECRET_KEY"] = "your_unique_key_here"  # Wygeneruj unikalny klucz
app.config["SESSION_TYPE"] = "filesystem"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"  # Ścieżka do bazy danych SQLite
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
Session(app)
db = SQLAlchemy(app)

# Dane użytkowników
users = {
    "Tomek": bcrypt.generate_password_hash("password1").decode("utf-8"),
    "Mateusz": bcrypt.generate_password_hash("password2").decode("utf-8"),
    "Dawid": bcrypt.generate_password_hash("password3").decode("utf-8"),
}

# Model bazy danych dla projektów
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    prefix = db.Column(db.String(10), nullable=False)
    current_number = db.Column(db.Integer, default=1)

# Inicjalizacja bazy danych
with app.app_context():
    db.create_all()

    # Dodanie przykładowych projektów
    if not Project.query.filter_by(name="Bialystok Rozwijany").first():
        db.session.add(Project(name="Bialystok Rozwijany", prefix="WK.B."))
    if not Project.query.filter_by(name="Kielce Ekspedycja").first():
        db.session.add(Project(name="Kielce Ekspedycja", prefix="WK.KA."))
    db.session.commit()

# Strona główna
@app.route("/")
def index():
    return render_template("index.html", projects=Project.query.all())

# Logowanie
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    username = data.get("username")
    password = data.get("password")
    
    if username in users and bcrypt.check_password_hash(users[username], password):
        session["user"] = username
        return jsonify({"message": "Login successful"})
    
    return jsonify({"error": "Invalid credentials"}), 401

# Generowanie sygnatury dla projektu
@app.route("/generate/<int:project_id>", methods=["GET"])
def generate(project_id):
    user = session.get("user")
    if not user:
        return jsonify({"error": "User session expired, please log in again"}), 401

    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    # Aktualizacja licznika w bazie danych
    with db.session.begin_nested():
        signature = f"{project.prefix}{str(project.current_number).zfill(4)}"
        project.current_number += 1
        db.session.commit()

    return jsonify({"user": user, "project": project.name, "signature": signature})

# Wylogowanie
@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"message": "Logged out successfully"})

if __name__ == "__main__":
    app.run(debug=True)
