from flask import Blueprint, Response
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, CollectorRegistry, generate_latest, multiprocess

from aquila.settings import PROMETHEUS_MULTIPROC_DIR

bp = Blueprint("metrics", __name__)


@bp.get("/metrics")
def metrics() -> Response:
    registry = REGISTRY
    if PROMETHEUS_MULTIPROC_DIR:  # pragma: no cover
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)

    headers = {"Content-Type": CONTENT_TYPE_LATEST}
    return Response(generate_latest(registry), status=200, headers=headers)
