from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import LoginManager, login_required, current_user, login_user
from backend.database import db
from backend.models import ActivityLog, User, CodeHistory, Feedback
from backend.auth import auth
from datetime import datetime
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash
import requests

# ✅ NEW IMPORTS FOR ENV
from dotenv import load_dotenv
import os

load_dotenv()

# ---------------- APP CONFIG ----------------

import os
from flask import Flask

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "../templates"),
    static_folder=os.path.join(BASE_DIR, "../static")
)

app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

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

        print("Default admin created")

# ---------------- HUGGING FACE TOKEN ----------------

# ✅ SECURE TOKEN FROM ENV
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
                "content": f"""
Generate clean runnable {language} code.

After the code write exactly:

EXPLANATION:

Then explain the code step by step.
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 800
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()

        if "choices" in result:
            return result["choices"][0]["message"]["content"]

        return "Error generating code."

    except Exception as e:
        return str(e)

# ---------------- EXPLAIN ONLY ----------------

def explain_only(prompt, language):
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
                "content": """
Explain the code step by step using numbered points.
Give a small example.
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 700
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()

        if "choices" in result:
            return result["choices"][0]["message"]["content"]

        return "Error generating explanation."

    except Exception as e:
        return str(e)

# ---------------- ROUTES ----------------

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/select-role')
def select_role():
    return render_template('select_role.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and email == "admin@gmail.com" and check_password_hash(user.password, password):
            login_user(user)
            log_activity(user.email, "admin_login")
            return redirect(url_for("admin_dashboard"))

        return "Invalid Admin Credentials"

    return render_template("admin_login.html")

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.email == "admin@gmail.com":
        return redirect(url_for("admin_dashboard"))

    return render_template('dashboard.html', user=current_user)

@app.route('/admin')
@login_required
def admin_dashboard():

    total_users = User.query.filter_by(role="user").count()
    total_generations = CodeHistory.query.count()
    total_feedback = Feedback.query.count()

    avg_rating = db.session.query(func.avg(Feedback.rating)).scalar()

    top_language = db.session.query(
        CodeHistory.language,
        func.count(CodeHistory.language)
    ).group_by(CodeHistory.language).order_by(
        func.count(CodeHistory.language).desc()
    ).first()

    logs = CodeHistory.query.order_by(CodeHistory.id.desc()).limit(10).all()
    users_list = User.query.filter_by(role="user").all()
    feedback_list = Feedback.query.order_by(Feedback.id.desc()).all()

    daily_usage = db.session.query(
        func.date(CodeHistory.timestamp),
        func.count(CodeHistory.id)
    ).group_by(func.date(CodeHistory.timestamp)).all()

    usage_dates = [str(i[0]) for i in daily_usage]
    usage_counts = [i[1] for i in daily_usage]

    language_usage = db.session.query(
        CodeHistory.language,
        func.count(CodeHistory.language)
    ).group_by(CodeHistory.language).all()

    languages = [i[0] for i in language_usage]
    language_counts = [i[1] for i in language_usage]

    return render_template(
        "admin_dashboard.html",
        users=total_users,
        generations=total_generations,
        feedbacks=total_feedback,
        avg_rating=round(avg_rating or 0, 1),
        top_language=top_language[0] if top_language else "None",
        logs=logs,
        users_list=users_list,
        feedback_list=feedback_list,
        usage_dates=usage_dates,
        usage_counts=usage_counts,
        languages=languages,
        language_counts=language_counts
    )

@app.route('/generate', methods=['POST'])
@login_required
def generate():
    prompt = request.form.get("prompt")
    language = request.form.get("language")

    log_activity(current_user.email, "generate", language)

    response = generate_code(prompt, language)

    if "EXPLANATION:" in response:
        parts = response.split("EXPLANATION:")
        code = parts[0].strip()
        explanation = parts[1].strip()
    else:
        code = response
        explanation = "Explanation not available"

    history = CodeHistory(
        user_id=current_user.id,
        prompt=prompt,
        language=language,
        generated_code=code,
        timestamp=datetime.now()
    )

    db.session.add(history)
    db.session.commit()

    return render_template(
        "dashboard.html",
        user=current_user,
        prompt=prompt,
        output=code,
        explanation=explanation
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