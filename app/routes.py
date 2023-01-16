from flask import render_template, flash, redirect, url_for, request, jsonify, session
from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse

rooms = [
    {"navn": "toilet", "pris": 15000},
    {"navn": "stue", "pris": 12000},
    {"navn": "køkken", "pris": 20000},
]

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html', title='Home', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now registered')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/pakker')
def pakker():
    return render_template("pakker.html", title="Pakker")

@app.route('/rum')
def rum():
    return render_template("rum.html", title="Rum", rooms=rooms)

@app.route('/om')
def om():
    return render_template("om.html", title="Om")

@app.route('/kontakt')
def kontakt():
    return render_template("kontakt.html", title="Kontakt")

@app.route('/api/kurv', methods=['GET', 'POST'])
def kurv():
    session['kurv'] = request.json['navn']
    print(session.get('kurv', 'not set'))
    return jsonify({'din': 'mor'})
