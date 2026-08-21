from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/apply")
def apply():
    return render_template("apply.html")

@app.route("/recruit")
def recruit():
    return render_template("recruit.html")

if __name__ == "__main__":
    app.run(debug=True)
    