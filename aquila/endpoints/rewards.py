import logging

from flask import Blueprint, render_template, request
from flask.templating import render_template_string
from werkzeug.exceptions import BadRequest

from aquila.blob_storage import template_loader
from aquila.polaris_request import get_polaris_reward

bp = Blueprint("rewards", __name__, template_folder="templates")
logger = logging.getLogger(__name__)


@bp.get("/reward")
def reward() -> str:
    retailer_slug: str | None = request.args.get("retailer")
    reward_id: str | None = request.args.get("reward")
    if not (retailer_slug and reward_id):
        logger.info("Missing required query params. Info: retailer: '%s', reward: '%s'", retailer_slug, reward_id)
        raise BadRequest

    reward_data = get_polaris_reward(retailer_slug, reward_id)
    template_slug: str = reward_data.pop("template_slug", "N/A")

    template = template_loader.get_template(template_slug)
    if template:
        logger.debug("rendering template from blob storage")
        return render_template_string(template, **reward_data)

    logger.debug("template not found for '%s' falling back to default.html", template_slug)
    return render_template("default.html", **reward_data)
