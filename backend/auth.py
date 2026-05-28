from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Deck, Card, create_decks_for_new_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta

def register_auth_routes(app):

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            if current_user.username == 'Joseph Mercy Buela' or current_user.username == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))

        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            user = User.query.filter_by(username=username).first()

            if user and check_password_hash(user.password, password):
                login_user(user)

                today = date.today()
                last_study = user.last_study_date

                if last_study:
                    try:
                        if isinstance(last_study, str):
                            last_study = datetime.fromisoformat(last_study).date()
                    except:
                        last_study = None

                if last_study == today:
                    pass
                elif last_study == today - timedelta(days=1):
                    user.streak = (user.streak or 0) + 1
                elif last_study is None:
                    user.streak = 1
                else:
                    user.streak = 1

                user.last_study_date = today.isoformat()
                db.session.commit()

                flash(f'Welcome back, {username}!', 'success')

                if user.username == 'Joseph Mercy Buela' or user.username == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')

        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            if current_user.username == 'Joseph Mercy Buela' or current_user.username == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))

        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

            if not username or not email or not password:
                flash('All fields are required!', 'error')
                return render_template('register.html')

            if password != confirm_password:
                flash('Passwords do not match!', 'error')
                return render_template('register.html')

            if len(password) < 4:
                flash('Password must be at least 4 characters!', 'error')
                return render_template('register.html')

            if User.query.filter_by(username=username).first():
                flash(f'Username "{username}" already exists!', 'error')
                return render_template('register.html')

            if User.query.filter_by(email=email).first():
                flash(f'Email "{email}" already registered!', 'error')
                return render_template('register.html')

            try:
                new_user = User(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    total_points=0,
                    total_studied=0,
                    streak=0,
                    unlocked_decks=999,
                    stars=0
                )
                db.session.add(new_user)
                db.session.flush()

                # Create decks for the new user
                create_decks_for_new_user(new_user.id)

                db.session.commit()

                flash(f'Registration successful! Welcome {username}! You now have 20 Python course decks.', 'success')
                return redirect(url_for('login'))

            except Exception as e:
                db.session.rollback()
                print(f"Registration error: {e}")
                flash('Registration failed. Please try again.', 'error')
                return render_template('register.html')

        return render_template('register.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))
