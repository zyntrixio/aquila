import logging

from datetime import datetime, timezone

from flask import Blueprint, abort, render_template, request
from flask.templating import render_template_string

from aquila.blob_storage import template_loader
from aquila.metrics import reward_requests_total
from aquila.polaris_request import get_polaris_reward

bp = Blueprint("rewards", __name__, template_folder="templates")
logger = logging.getLogger(__name__)


@bp.get("/reward")
def reward() -> str:
    retailer_slug: str | None = request.args.get("retailer")
    reward_id: str | None = request.args.get("reward")
    if not (retailer_slug and reward_id):
        logger.info("Missing required query params. Info: retailer: '%s', reward: '%s'", retailer_slug, reward_id)
        reward_requests_total.labels(
            retailer_slug=retailer_slug or "N/A",
            response_status=400,
            response_template="N/A",
        ).inc()
        abort(400)

    reward_data = get_polaris_reward(retailer_slug, reward_id)
    reward_data.update(
        {
            "expiry_date": datetime.strptime(reward_data["expiry_date"], "%Y-%m-%d")
            .replace(tzinfo=timezone.utc)
            .strftime("%d/%m/%Y")
        }
    )
    template_slug: str = reward_data.pop("template_slug", "N/A")

    if template := template_loader.get_template(retailer_slug, template_slug):
        logger.debug("rendering template from blob storage")
        reward_requests_total.labels(
            retailer_slug=retailer_slug, response_status=200, response_template=template_slug
        ).inc()
        # deepcode ignore XSS: source is a trusted internal tool
        return render_template_string(template, **reward_data)

    logger.debug("template not found for '%s' falling back to default.html", template_slug)
    reward_requests_total.labels(retailer_slug=retailer_slug, response_status=200, response_template="default").inc()
    return render_template("default.html", **reward_data)
