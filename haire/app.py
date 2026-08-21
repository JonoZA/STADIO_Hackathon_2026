from flask import Flask, render_template

app = Flask(__name__)

<<<<<<< HEAD

@app.route("/recruit")
def recruit():
    return render_template("recruit.html")

=======
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def apply():
    return render_template("apply.html")

@app.route("/submit", methods=["POST"])
def recruit
>>>>>>> 034ec03 (started with routing)

if __name__ == "__main__":
    app.run(debug=True)
    