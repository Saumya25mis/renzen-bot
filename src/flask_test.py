# pylint: disable=import-error
"""Test Response."""

from flask import Flask

app = Flask(__name__)
app.config["SECRET_KEY"] = "temp--secret--key"


@app.route("/")
def hello_world():
    """Return Hello World."""
    return "<h1>Hello World</h1>", 200


if __name__ == "__main__":
    WEBSITE_URL = "api2.renzen.io:80"  # for subdomain support
    app.config["SERVER_NAME"] = WEBSITE_URL
    app.run(debug=True, port=80)
