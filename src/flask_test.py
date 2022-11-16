# pylint: disable=import-error
"""Test Response."""

from flask import Flask

app = Flask(__name__)
app.config["SECRET_KEY"] = "temp--secret--key"


@app.route("/", methods=["GET", "POST"])
def hello_world():
    """Return Hello World."""
    return "<h1>Hello World</h1>"


if __name__ == "__main__":
    app.run(debug=True)
