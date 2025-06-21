from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lines.db'
db = SQLAlchemy(app)

class Line(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    japanese = db.Column(db.String(200), nullable=False)
    romaji = db.Column(db.String(200), nullable=True)
    translation = db.Column(db.String(200), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed = db.Column(db.Boolean, default=False)

@app.route('/')
def index():
    current_line = Line.query.filter_by(reviewed=False).first()
    return render_template('index.html', line=current_line)

@app.route('/add', methods=['GET', 'POST'])
def add_line():
    if request.method == 'POST':
        new_line = Line(
            japanese=request.form['japanese'],
            romaji=request.form['romaji'],
            translation=request.form['translation']
        )
        db.session.add(new_line)
        db.session.commit()
        return redirect('/')
    return render_template('add_line.html')

@app.route('/next')
def next_line():
    line = Line.query.filter_by(reviewed=False).first()
    if line:
        line.reviewed = True
        db.session.commit()
    return redirect('/')

@app.route('/history')
def history():
    lines = Line.query.filter_by(reviewed=True).order_by(Line.date_added.desc()).all()
    return render_template('history.html', lines=lines)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
