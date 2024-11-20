import os 

from flask import Flask

from .routes import main
from flask_mongoengine import MongoEngine


def create_app():
    app = Flask(__name__)
    
    app.config["MONGODB_SETTINGS"] = {
    "host": "mongodb+srv://lakshmanreddy458:CO4BzJ3Xo2NFEb8z@taskmaster.0ygad.mongodb.net/mydatabase?retryWrites=true&w=majority"
}
    db = MongoEngine(app)

    app.register_blueprint(main)

    return app