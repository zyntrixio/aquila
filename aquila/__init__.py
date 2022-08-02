from flask import Flask, abort, request

from aquila._version import __version__
from aquila.endpoints.healthz import bp as healthz_bp
from aquila.endpoints.metrics import bp as metrics_bp
from aquila.endpoints.rewards import bp as rewards_bp
from aquila.settings import METRICS_DEBUG, PROJECT_NAME


def check_metrics_port() -> None:
    port = request.server[1] if request.server else None
    path = request.path

    if (port == 9100 and path != "/metrics") or (port != 9100 and path == "/metrics" and not METRICS_DEBUG):
        abort(404)


def create_app() -> Flask:
    app = Flask(PROJECT_NAME)
    app.register_blueprint(rewards_bp)
    app.register_blueprint(healthz_bp)
    app.register_blueprint(metrics_bp)

    app.before_request(check_metrics_port)

    return app
