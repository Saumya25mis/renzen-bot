"""Test Response."""

# pylint: disable=import-error

from flask import Flask

app = Flask(__name__)
app.config["SECRET_KEY"] = "temp--secret--key"


@app.route("/", methods=["GET", "POST"])
def hello_world():
    """Return Hello World."""
    return "Hello World"
