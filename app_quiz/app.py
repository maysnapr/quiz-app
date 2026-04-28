from flask import Flask, render_template, request, redirect, session
import sqlite3
import requests
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

# REGISTER
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        db = get_db()
        db.execute("INSERT INTO users (username, password) VALUES (?,?)",
                   (request.form['username'], request.form['password']))
        db.commit()
        return redirect('/login')
    return render_template('register.html')

# LOGIN
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

# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

# ================= QUIZ =================
@app.route('/quiz')
def quiz():
    url = "https://opentdb.com/api.php?amount=5&type=multiple"

    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        questions_raw = data.get('results', [])
    except:
        questions_raw = []

    questions = []

    for q in questions_raw:
        question = html.unescape(q['question'])
        correct = html.unescape(q['correct_answer'])
        incorrect = [html.unescape(ans) for ans in q['incorrect_answers']]

        options = incorrect + [correct]
        random.shuffle(options)

        questions.append({
            "question": question,
            "options": options,
            "correct_answer": correct
        })

    # 🔥 fallback kalau API gagal (biar tidak kosong saat demo)
    if not questions:
        questions = [
            {
                "question": "Apa ibu kota Indonesia?",
                "options": ["Jakarta", "Bandung", "Surabaya", "Medan"],
                "correct_answer": "Jakarta"
            },
            {
                "question": "2 + 2 = ?",
                "options": ["3", "4", "5", "6"],
                "correct_answer": "4"
            }
        ]

    return render_template('quiz.html', questions=questions)

# ================= SUBMIT =================
@app.route('/submit', methods=['POST'])
def submit():
    score = 0
    review = []

    for key in request.form:
        if key.startswith("question_"):
            q_num = key.split("_")[1]

            question = request.form.get(f"text_{q_num}")
            user_answer = request.form.get(key)
            correct_answer = request.form.get(f"correct_{q_num}")

            is_correct = user_answer == correct_answer

            if is_correct:
                score += 1

            review.append({
                "question": question,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct
            })

    db = get_db()
    db.execute("INSERT INTO quiz_results (user_id, score) VALUES (?,?)",
               (session['user_id'], score))
    db.commit()

    return render_template('result.html', score=score, review=review)

# ================= LEADERBOARD =================
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

# ================= RUN =================
if __name__ == '__main__':
    app.run(debug=True)