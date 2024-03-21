import os

from dotenv import load_dotenv
from flask import Flask
from flask_pymongo import PyMongo


load_dotenv()

# Configure app (database, secret key, etc.)
MONGO_URI = os.environ.get("MONGO_URI")


def create_app():
    app = Flask(__name__)
    app.config["MONGO_URI"] = MONGO_URI

    mongo = PyMongo(app)

    from activitypub import register_activitypub_blueprint
    from authentication import register_auth_blueprint

    register_activitypub_blueprint(app, mongo)
    register_auth_blueprint(app, mongo)

    return app
