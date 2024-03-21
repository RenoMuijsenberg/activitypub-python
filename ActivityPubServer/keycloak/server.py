from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/api/public")
def public():
    return jsonify(message="Hello from a public endpoint! You don't need to be authenticated to see this.")


@app.route("/api/private")
def private():
    return jsonify(message="Hello from a private endpoint! You need to be authenticated to see this.")


@app.route("/api/private-scoped")
def private_scoped():
    return jsonify(
        message="Hello from a private endpoint! You need to be authenticated and have a scope of read:messages to see this.")


app.run(host="0.0.0.0", port=5000, debug=True)