from flask import Flask, render_template, request, redirect

app = Flask(__name__)

FILE_NAME = "students.txt"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        roll = request.form["roll"]
        name = request.form["name"]
        marks = request.form["marks"]

        with open(FILE_NAME, "a") as f:
            f.write(f"{roll},{name},{marks}\n")

        return redirect("/display")

    return render_template("add.html")

@app.route("/display")
def display_students():
    students = []

    try:
        with open(FILE_NAME, "r") as f:
            for line in f:
                roll, name, marks = line.strip().split(",")
                students.append((roll, name, marks))
    except FileNotFoundError:
        pass

    return render_template("display.html", students=students)

if __name__ == "__main__":
    app.run(debug=True)
