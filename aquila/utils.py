import logging

import requests

from werkzeug.exceptions import NotFound, ServiceUnavailable

from aquila.settings import POLARIS_BASE_URL

logger = logging.getLogger(__name__)


def get_polaris_reward(retailer_slug: str, reward_id: str) -> dict:
    """
    expected response payload from polaris will be:
    ```json
    {
        "code": "Reward redeeming code",
        "expiry_date": "2022-05-18",
        "template_slug": "name of template to use"
        "pin": "Optional field"
    }
    """
    try:
        response = requests.get(f"{POLARIS_BASE_URL}/{retailer_slug}/reward/{reward_id}")
    except Exception as ex:
        logger.exception("Unable to reach polaris", exc_info=ex)
        raise ServiceUnavailable from ex

    if response.status_code != 200:
        logger.info("Received negative response from polaris. Info: response: %s", response.text)
        raise NotFound

    return response.json()
