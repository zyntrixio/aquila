from flask import Flask

from app.endpoints import bp
from app.settings import PROJECT_NAME


def create_app() -> Flask:
    app = Flask(PROJECT_NAME)
    app.register_blueprint(bp)

    return app
