from flask_login import UserMixin
from datetime import datetime
from backend.database import db

class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100))

    email = db.Column(db.String(100), unique=True)

    password = db.Column(db.String(200))
    role = db.Column(db.String(20), default="user")

    created_at = db.Column(db.DateTime, default=datetime.now)

    last_active = db.Column(db.DateTime)

class CodeHistory(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer)

    prompt = db.Column(db.Text)

    language = db.Column(db.String(50))

    generated_code = db.Column(db.Text)

    timestamp = db.Column(db.DateTime, default=datetime.now)


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120))
    user_name = db.Column(db.String(120))
    rating = db.Column(db.Integer)
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime)

class LoginHistory(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer)

    login_time = db.Column(db.DateTime)

class ActivityLog(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_email = db.Column(db.String(100))

    action = db.Column(db.String(50))

    language = db.Column(db.String(50))

    created_at = db.Column(db.DateTime)