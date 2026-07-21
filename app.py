from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"

# =========================
# DATABASE
# =========================
def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# REGISTER
# =========================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users(name,email,password) VALUES(?,?,?)",
                (name, email, password)
            )

            conn.commit()
            conn.close()

            return redirect("/login")

        except:
            conn.close()
            return "Email already exists!"

    return render_template("register.html")


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cur.fetchone()
        conn.close()

        if user:
            session["user"] = user[1]
            return redirect("/dashboard")

    return render_template("login.html")


# =========================
# DASHBOARD
# =========================
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        name=session["user"]
    )


# =========================
# RESUME UPLOAD
# =========================
@app.route("/resume", methods=["GET", "POST"])
def resume():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":

        if "resume" not in request.files:
            return render_template("resume.html", msg="Choose file first")

        file = request.files["resume"]

        if file.filename == "":
            return render_template("resume.html", msg="Choose file first")

        if not os.path.exists("uploads"):
            os.makedirs("uploads")

        path = os.path.join("uploads", file.filename)
        file.save(path)

        import random
        score = random.randint(65, 95)

        session["score"] = score

        return render_template(
            "resume.html",
            msg="Resume Uploaded Successfully!",
            score=score
        )

    return render_template("resume.html")
        

# =========================
# VIEW SCORE
# =========================
@app.route("/score")
def score():

    if "user" not in session:
        return redirect("/login")

    s = session.get("score", 0)

    return render_template(
        "score.html",
        score=s
    )


# =========================
# MOCK INTERVIEW
# =========================
@app.route("/mock_interview", methods=["GET", "POST"])
def mock_interview():

    if "user" not in session:
        return redirect("/login")

    all_questions = {

        "Python Developer": [
            "What is Python?",
            "What is List?",
            "What is Tuple?",
            "Explain OOP.",
            "What is Flask?"
        ],

        "Data Analyst": [
            "What is SQL?",
            "What is Excel?",
            "What is Power BI?",
            "What is Data Cleaning?",
            "What is Dashboard?"
        ],

        "Java Developer": [
            "What is Java?",
            "What is JVM?",
            "What is Inheritance?",
            "What is Method Overloading?",
            "What is Encapsulation?"
        ],

        "HR Round": [
            "Tell me about yourself.",
            "Why should we hire you?",
            "What are your strengths?",
            "Where do you see yourself in 5 years?",
            "Why do you want this job?"
        ],

        "AI/ML Developer": [
            "What is Machine Learning?",
            "What is Overfitting?",
            "What is Regression?",
            "Difference between supervised and unsupervised learning?",
            "Which libraries are used in ML?"
        ],

        "Data Science Engineer": [
            "What is Data Science?",
            "What is Pandas?",
            "What is NumPy?",
            "What is Feature Engineering?",
            "Role of Statistics in Data Science?"
        ]
    }

    role = request.form.get(
        "role",
        session.get("role", "")
    )

    result = ""
    score = 0
    user_answer = ""

    if role:
        session["role"] = role

    if "q_index" not in session:
        session["q_index"] = 0

    if request.method == "POST":

        action = request.form.get("action")

        # NEXT QUESTION
        if action == "next":
            session["q_index"] += 1

        # SUBMIT ANSWER
        else:

            user_answer = request.form.get(
                "answer",
                ""
            )

            if len(user_answer) > 100:
                result = "Excellent Answer"
                score = 9

            elif len(user_answer) > 50:
                result = "Good Answer"
                score = 7

            elif len(user_answer) > 20:
                result = "Average Answer"
                score = 5

            else:
                result = "Need Improvement"
                score = 3

    question = ""

    if role in all_questions:

        questions = all_questions[role]

        if session["q_index"] >= len(questions):
            session["q_index"] = 0

        question = questions[
            session["q_index"]
        ]

    return render_template(
        "mock_interview.html",
        roles=all_questions.keys(),
        role=role,
        question=question,
        result=result,
        score=score,
        user_answer=user_answer
    )


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5050,
        debug=True
    )