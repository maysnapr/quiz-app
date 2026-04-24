from flask import Flask, render_template, request, redirect, session
import sqlite3
import requests
from googletrans import Translator
import html
import random

app = Flask(__name__)
app.secret_key = 'secretkey'

# ================= DATABASE =================
def get_db():
    return sqlite3.connect('database.db')

def init_db():
    db = get_db()
    db.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )''')

    db.execute('''CREATE TABLE IF NOT EXISTS quiz_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        score INTEGER,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    db.commit()

init_db()

# ================= ROUTES =================
@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        db = get_db()
        db.execute("INSERT INTO users (username, password) VALUES (?,?)",
                   (request.form['username'], request.form['password']))
        db.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=? AND password=?",
                          (request.form['username'], request.form['password'])).fetchone()
        if user:
            session['user_id'] = user[0]
            return redirect('/dashboard')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

@app.route('/quiz')
def quiz():
    url = "https://opentdb.com/api.php?amount=5&type=multiple"
    data = requests.get(url).json()

    translator = Translator()
    questions = data['results']

    for q in questions:
        # decode HTML
        question = html.unescape(q['question'])
        correct = html.unescape(q['correct_answer'])
        incorrect = [html.unescape(ans) for ans in q['incorrect_answers']]

        # translate ke Indonesia
        q['question'] = translator.translate(question, dest='id').text
        q['correct_answer'] = translator.translate(correct, dest='id').text
        q['incorrect_answers'] = [translator.translate(ans, dest='id').text for ans in incorrect]

        # gabung & acak jawaban
        q['options'] = q['incorrect_answers'] + [q['correct_answer']]
        random.shuffle(q['options'])

    return render_template('quiz.html', questions=questions)

@app.route('/submit', methods=['POST'])
def submit():
    score = 0

    for key in request.form:
        if key.startswith("question_"):
            q_num = key.split("_")[1]
            user_answer = request.form.get(key)
            correct_answer = request.form.get(f"correct_{q_num}")

            if user_answer == correct_answer:
                score += 1

    db = get_db()
    db.execute("INSERT INTO quiz_results (user_id, score) VALUES (?,?)",
               (session['user_id'], score))
    db.commit()

    return render_template('result.html', score=score)

@app.route('/leaderboard')
def leaderboard():
    db = get_db()
    data = db.execute("""
        SELECT users.username, quiz_results.score, quiz_results.date
        FROM quiz_results
        JOIN users ON users.id = quiz_results.user_id
        ORDER BY score DESC
    """).fetchall()

    return render_template('leaderboard.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)