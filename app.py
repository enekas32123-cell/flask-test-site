from flask import Flask, render_template, request, redirect, session
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # для сесій

# Файл Excel
DATA_FILE = "data.xlsx"
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["ПІБ", "Email", "Тест", "Питання", "Відповідь", "Правильна"])
    df.to_excel(DATA_FILE, index=False)

# Тести
tests = {
    "test1": [
        {"q": "Що було у відео?", "options": ["Дрон", "Кіт", "Авто"], "correct": "Дрон"},
        {"q": "Який колір мав об’єкт?", "options": ["Червоний", "Синій", "Зелений"], "correct": "Червоний"},
    ],
    "test2": [
        {"q": "Що робив дрон?", "options": ["Летів", "Стояв", "Плавав"], "correct": "Летів"},
        {"q": "Яка була мета польоту?", "options": ["Зйомка", "Змагання", "Розвага"], "correct": "Зйомка"},
    ],
}


@app.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form["fullname"]
        email = request.form["email"]

        # Простенька перевірка email
        if "@" not in email or "." not in email:
            return render_template("register.html", error="Неправильний email!")

        session["fullname"] = fullname
        session["email"] = email
        session["step"] = 1
        return redirect("/video/1")

    return render_template("register.html", error=None)


@app.route("/video/<int:num>")
def video(num):
    if "fullname" not in session:
        return redirect("/")

    if num > 2:
        return render_template("result.html", name=session["fullname"])

    video_src = f"/static/video{num}.mp4"
    return render_template("video.html", video_src=video_src, num=num)


@app.route("/test/<int:num>", methods=["GET", "POST"])
def test(num):
    if "fullname" not in session:
        return redirect("/")

    test_key = f"test{num}"
    questions = tests[test_key]

    if request.method == "POST":
        answers = []
        for i, q in enumerate(questions):
            user_answer = request.form.get(f"q{i}")
            correct = q["correct"]
            answers.append((q["q"], user_answer, correct))

        # Зберігаємо в Excel
        df = pd.read_excel(DATA_FILE)
        for q_text, ans, corr in answers:
            df.loc[len(df)] = [session["fullname"], session["email"], test_key, q_text, ans, corr]
        df.to_excel(DATA_FILE, index=False)

        # Переходимо до наступного відео або завершення
        if num == 1:
            return redirect("/video/2")
        else:
            return redirect("/finish")

    return render_template("test.html", num=num, questions=questions)


@app.route("/finish")
def finish():
    return render_template("result.html", name=session["fullname"])


if __name__ == "__main__":
    app.run(debug=True)
