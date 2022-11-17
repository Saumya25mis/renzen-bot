# pylint: disable=import-error
"""Test Response."""

from flask import Flask

app = Flask(__name__)
app.config["SECRET_KEY"] = "temp--secret--key"


@app.route("/")
def hello_world():
    """Return Hello World."""
    return "<h1>Hello World</h1>", 200


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):  # pylint: disable=unused-argument
    """Catch all requests."""
    return "<h1>Caught It!</h1>", 200


if __name__ == "__main__":
    # WEBSITE_URL = "renzen.io:80"  # for subdomain support
    # app.config["SERVER_NAME"] = WEBSITE_URL
    app.run(debug=True, port=80, host="0.0.0.0")
