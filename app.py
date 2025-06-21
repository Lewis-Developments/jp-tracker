from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lines.db'
app.secret_key = os.environ.get('SECRET_KEY', 'dev')
db = SQLAlchemy(app)

class Line(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    japanese = db.Column(db.String(200), nullable=False)
    romaji = db.Column(db.String(200), nullable=True)
    translation = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    song = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed = db.Column(db.Boolean, default=False)


# --- LOGIN ROUTE ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        passcode = request.form.get('passcode')
        if passcode == os.environ.get('PASSCODE'):
            session['logged_in'] = True
            return redirect('/')
        else:
            error = 'Incorrect passcode.'
    return render_template('login.html', error=error)

# --- LOGOUT ROUTE ---
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')

# --- LOGIN REQUIRED DECORATOR ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
@login_required
def index():
    current_line = Line.query.filter_by(reviewed=False).first()
    return render_template('index.html', line=current_line)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_line():
    if request.method == 'POST':
        new_line = Line(
            japanese=request.form['japanese'],
            romaji=request.form['romaji'],
            translation=request.form['translation'],
            artist=request.form['artist'],
            song=request.form['song']
        )
        db.session.add(new_line)
        db.session.commit()
        return redirect('/')
    return render_template('add_line.html')


@app.route('/next')
@login_required
def next_line():
    line = Line.query.filter_by(reviewed=False).first()
    if line:
        line.reviewed = True
        db.session.commit()
    return redirect('/')

@app.route('/history')
@login_required
def history():
    lines = Line.query.filter_by(reviewed=True).order_by(Line.date_added.desc()).all()
    return render_template('history.html', lines=lines)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
