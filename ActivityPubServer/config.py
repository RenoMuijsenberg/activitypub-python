import os

from dotenv import load_dotenv
from flask import Flask
from flask_pymongo import PyMongo
from activitypub import webfinger, actor, outbox, inbox

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["MONGO_URI"] = os.environ.get("MONGO_URI")

    mongo = PyMongo(app)

    webfinger.register_webfinger_blueprint(app, mongo)
    actor.register_actor_blueprint(app, mongo)
    outbox.register_outbox_blueprint(app, mongo)
    inbox.register_inbox_blueprint(app, mongo)

    return app
