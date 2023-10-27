from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def first_example_page():
    return render_template("Base.html")


app.run(debug=True)