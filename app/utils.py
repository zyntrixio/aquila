import requests

from requests.adapters import HTTPAdapter, Retry
from werkzeug.exceptions import NotFound

from app.settings import POLARIS_BASE_URL


def request_with_retry() -> requests.Session:
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session


def get_polaris_reward(retailer_slug: str, reward_id: str) -> dict:
    """
    expected response payload from polaris will be:
    ```json
    {
        "code": "Reward redeeming code",
        "expiry_date": "2022-05-18",
        "template_slug": "name of template to use"
    }
    """

    response = request_with_retry().get(f"{POLARIS_BASE_URL}/{retailer_slug}/reward/{reward_id}")
    if response.status_code != 200:
        raise NotFound("nope")

    return response.json()
