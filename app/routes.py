from flask import render_template, flash, redirect, url_for, request, jsonify, session
from app import app, db
from app.forms import LoginForm, RegistrationForm, Betaling_f
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Betaling
from werkzeug.urls import url_parse

rooms = [
    {"navn": "toilet", "pris": 15000, "beskrivelse": "Et toilet med løbende vand da den bliver koblet op med dit vandværk."},
    {"navn": "stue", "pris": 12000, "beskrivelse": "Et rum med 2 stikontakter og plads til en sofa"},
    {"navn": "køkken", "pris": 20000, "beskrivelse": "Et rum med 3 stikontankter som bliver koblet op med dit vandværk"},
    {"navn": "kontor", "pris": 10000, "beskrivelse": "Et mindre rum med 2 stikkontankter og plads til et skrivebord"},
    {"navn": "soveværelse", "pris": 10000, "beskrivelse": "Et rum med plads til et par senge"},
]

pakke_lst = [
    [rooms[0], rooms[1]],
    [rooms[0], rooms[1], rooms[2]],
    [rooms[0], rooms[1], rooms[2], rooms[3]],
]

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
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
    return render_template("pakker.html", title="Pakker", pakker=pakke_lst)

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
    if not session.get('kurv'):
        session['kurv'] = []
    kurv_list = session['kurv']
    # kurv_list.append(request.json['navn'])
    for navn in request.json['navn']:
        kurv_list.append(navn)
    session['kurv'] = kurv_list
    print(session['kurv'])
    return jsonify({"din": "mor"})

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if not session.get('kurv'):
        return render_template("kurv.html", title="kurv", tom=True)
    total = 0
    rum_kurv = []
    for rum in session['kurv']:
        for dicto in rooms:
            if dicto['navn'] == rum:
                total += dicto['pris']
                rum_kurv.append(dicto)
    session['total'] = total
    return render_template("kurv.html", title="Kurv", kurv=rum_kurv, total=total)

@app.route('/api/rkurv', methods=['GET', 'POST'])
def r_kurv():
    kurv_list = session['kurv']
    kurv_list.pop(int(request.json['id']) - 1)
    session['kurv'] = kurv_list
    return jsonify({"success": True})

@app.route('/produkt', methods=['GET', 'POST'])
def prod():
    is_pakke = False
    if request.args.get('name'):
        prod = {}
        for rum in rooms:
            if rum['navn'] == request.args.get('name'):
                prod = rum
                break
    elif request.args.get('id'):
        is_pakke = True
        prod = pakke_lst[int(request.args.get('id')) - 1]

    return render_template("produkt.html", title=request.args.get('name'), produkt=prod, is_pakke=is_pakke)

@app.route('/betal', methods=['GET', 'POST'])
def betal():
    form = Betaling_f()
    if form.validate_on_submit():
        kurv_str = ""
        for produkt in session['kurv']:
            kurv_str += f"{produkt}:"
        betaler = Betaling(adresse=form.adresse.data, kurv=kurv_str)
        db.session.add(betaler)
        db.session.commit()
        temp = session['kurv']
        session['betalt'] = temp
        temp = []
        session['kurv'] = temp
        return redirect(url_for('betalt'))
    return render_template("betal.html", title="Betal", form=form)

@app.route('/betalt')
def betalt():
    return render_template("betalt.html", title="Betalt")
