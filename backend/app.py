from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import LoginManager, login_required, current_user, login_user
from backend.database import db
from backend.models import ActivityLog, User, CodeHistory, Feedback
from backend.auth import auth
from datetime import datetime
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# ---------------- APP CONFIG ----------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "../templates"),
    static_folder=os.path.join(BASE_DIR, "../static")
)

app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'users.db')

db.init_app(app)

with app.app_context():
    db.create_all()

# ---------------- LOGIN MANAGER ----------------

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth)

# ---------------- CREATE DEFAULT ADMIN ----------------

def create_default_admin():
    admin = User.query.filter_by(email="admin@gmail.com").first()

    if not admin:
        admin_user = User(
            username="admin",
            email="admin@gmail.com",
            password=generate_password_hash("admin123"),
            role="admin",
            created_at=datetime.now()
        )
        db.session.add(admin_user)
        db.session.commit()

# ---------------- TOKEN ----------------

HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

# ---------------- ACTIVITY LOGGER ----------------

def log_activity(email, action, language=None):
    activity = ActivityLog(
        user_email=email,
        action=action,
        language=language,
        created_at=datetime.now()
    )
    db.session.add(activity)

    user = User.query.filter_by(email=email).first()
    if user:
        user.last_active = datetime.now()

    db.session.commit()

# ---------------- GENERATE CODE ----------------

def generate_code(prompt, language):
    try:
        url = "https://router.huggingface.co/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "Qwen/Qwen2.5-Coder-7B-Instruct",
            "messages": [
                {
                    "role": "system",
                    "content": f"Generate clean {language} code with explanation and example."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            return f"API Error: {response.text}"

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Error: {str(e)}"

# ---------------- EXPLAIN ONLY ----------------

def explain_only(prompt, language):
    try:
        url = "https://router.huggingface.co/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "Qwen/Qwen2.5-Coder-7B-Instruct",
            "messages": [
                {
                    "role": "system",
                    "content": "Explain clearly with step-by-step and example."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            return f"API Error: {response.text}"

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Error: {str(e)}"

# ---------------- ROUTES ----------------

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == "admin":
        return redirect(url_for("admin_dashboard"))

    return render_template('dashboard.html', user=current_user)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and user.role == "admin" and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("admin_dashboard"))

        return "Invalid Admin Credentials"

    return render_template("admin_login.html")

@app.route('/admin')
@login_required
def admin_dashboard():
    total_users = User.query.filter_by(role="user").count()
    total_generations = CodeHistory.query.count()
    total_feedback = Feedback.query.count()

    avg_rating = db.session.query(func.avg(Feedback.rating)).scalar()

    return render_template(
        "admin_dashboard.html",
        users=total_users,
        generations=total_generations,
        feedbacks=total_feedback,
        avg_rating=round(avg_rating or 0, 1)
    )

@app.route('/generate', methods=['POST'])
@login_required
def generate():
    prompt = request.form.get("prompt")
    language = request.form.get("language")

    log_activity(current_user.email, "generate", language)

    response = generate_code(prompt, language)

    history = CodeHistory(
        user_id=current_user.id,
        prompt=prompt,
        language=language,
        generated_code=response,
        timestamp=datetime.now()
    )

    db.session.add(history)
    db.session.commit()

    return render_template(
        "dashboard.html",
        user=current_user,
        output=response
    )

@app.route('/api/feedback', methods=['POST'])
@login_required
def submit_feedback():
    data = request.get_json()

    feedback = Feedback(
        user_email=current_user.email,
        user_name=current_user.username,
        rating=data.get("rating"),
        message=data.get("message") or data.get("tag"),
        created_at=datetime.now()
    )

    db.session.add(feedback)
    db.session.commit()

    return jsonify({"success": True})

# ---------------- MAIN ----------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_default_admin()

    app.run(debug=True)