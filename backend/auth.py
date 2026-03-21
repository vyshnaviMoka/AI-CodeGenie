from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required
from backend.models import User, LoginHistory
from backend.database import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

auth = Blueprint('auth', __name__)


# ---------------- REGISTER ----------------
@auth.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form.get('username')
        email = request.form.get('email')
        password = generate_password_hash(request.form.get('password'))

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already registered!"

        new_user = User(
            username=username,
            email=email,
            password=password,
            created_at=datetime.now(),
            last_active=datetime.now()
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template('register.html')


# ---------------- USER LOGIN ----------------
@auth.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            login_user(user)

            # update last active
            user.last_active = datetime.now()

            # save login history
            login_record = LoginHistory(
                user_id=user.id,
                login_time=datetime.now()
            )

            db.session.add(login_record)
            db.session.commit()

            return redirect(url_for('dashboard'))

        return "Invalid Email or Password"

    return render_template('login.html')


# ---------------- ADMIN LOGIN ----------------
@auth.route('/admin-login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and email == "admin@gmail.com" and check_password_hash(user.password, password):

            login_user(user)

            # update last active
            user.last_active = datetime.now()

            # save login history
            login_record = LoginHistory(
                user_id=user.id,
                login_time=datetime.now()
            )

            db.session.add(login_record)
            db.session.commit()

            return redirect(url_for('admin_dashboard'))

        return "Invalid Admin Credentials"

    return render_template('admin_login.html')


# ---------------- LOGOUT ----------------
@auth.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect(url_for('auth.login'))