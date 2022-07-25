from flask import Blueprint, render_template, request
from werkzeug.exceptions import NotFound

from app.utils import get_polaris_reward

bp = Blueprint("reward", __name__, template_folder="templates")


@bp.get("/reward")
def reward() -> str:
    retailer_slug: str | None = request.args.get("retailer")
    reward_id: str | None = request.args.get("reward")

    if not (retailer_slug and reward_id):
        raise NotFound("nope")

    reward_data = get_polaris_reward(retailer_slug, reward_id)
    return render_template("test.html", **reward_data)
