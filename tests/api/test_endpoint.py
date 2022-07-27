from datetime import date
from typing import TYPE_CHECKING
from uuid import uuid4

import responses

from flask import render_template, url_for
from pytest_mock import MockerFixture

from aquila.settings import POLARIS_BASE_URL

if TYPE_CHECKING:
    from flask.testing import FlaskClient


@responses.activate
def test_reward_ok(test_client: "FlaskClient", mocker: MockerFixture) -> None:

    code = "TSTRWDCODE1234"
    expiry_date = str(date.today())
    pin = "1234"

    template = """
    <p>{{ code }}</p>
    <p>{{ expiry_date }}</p>
    <p>{{ pin }}</p>
    """
    expected_response = f"""
    <p>{ code }</p>
    <p>{ expiry_date }</p>
    <p>{ pin }</p>
    """

    retailer_slug = "test-retailer"
    reward_id = str(uuid4())

    responses.get(
        f"{POLARIS_BASE_URL}/{retailer_slug}/reward/{reward_id}",
        json={
            "code": code,
            "expiry_date": expiry_date,
            "template_slug": "test-template",
            "pin": pin,
        },
    )
    mock_template_loader = mocker.patch("aquila.endpoints.rewards.template_loader")
    mock_template_loader.get_template.return_value = template
    resp = test_client.get(url_for("rewards.reward", retailer=retailer_slug, reward=reward_id))
    assert resp.text == expected_response


@responses.activate
def test_reward_fallback_template(test_client: "FlaskClient", mocker: MockerFixture) -> None:

    code = "TSTRWDCODE1234"
    expiry_date = str(date.today())
    pin = "1234"

    expected_response = render_template("default.html", code=code, expiry_date=expiry_date, pin=pin)

    retailer_slug = "test-retailer"
    reward_id = str(uuid4())

    responses.get(
        f"{POLARIS_BASE_URL}/{retailer_slug}/reward/{reward_id}",
        json={
            "code": code,
            "expiry_date": expiry_date,
            "template_slug": "test-template",
            "pin": pin,
        },
    )
    mock_template_loader = mocker.patch("aquila.endpoints.rewards.template_loader")
    mock_template_loader.get_template.return_value = None
    resp = test_client.get(url_for("rewards.reward", retailer=retailer_slug, reward=reward_id))
    assert resp.text == expected_response


def test_reward_missing_param(test_client: "FlaskClient") -> None:

    resp = test_client.get(url_for("rewards.reward", reward="Stuff"))
    assert resp.status_code == 400

    resp = test_client.get(url_for("rewards.reward", retailer="Stuff"))
    assert resp.status_code == 400

    resp = test_client.get(url_for("rewards.reward"))
    assert resp.status_code == 400


@responses.activate
def test_reward_polaris_negative_responses(test_client: "FlaskClient", mocker: MockerFixture) -> None:

    expected_response = render_template("default_error.html")

    retailer_slug = "test-retailer"
    reward_id = str(uuid4())

    # Polaris returned a 404
    responses.get(f"{POLARIS_BASE_URL}/{retailer_slug}/reward/{reward_id}", json={}, status=404)

    resp = test_client.get(url_for("rewards.reward", retailer=retailer_slug, reward=reward_id))
    assert resp.status_code == 404

    # Polaris returned a non 404 error state
    responses.get(f"{POLARIS_BASE_URL}/{retailer_slug}/reward/{reward_id}", json={}, status=500)

    resp = test_client.get(url_for("rewards.reward", retailer=retailer_slug, reward=reward_id))
    assert resp.text == expected_response

    # an exception happened while trying to contact polaris
    mock_requests = mocker.patch("aquila.polaris_request.requests")
    mock_requests.get.side_effect = Exception("random stuff happened")

    resp = test_client.get(url_for("rewards.reward", retailer=retailer_slug, reward=reward_id))
    assert resp.text == expected_response


@responses.activate
def test_reward_polaris_negative_response_retailer_error_template(
    test_client: "FlaskClient", mocker: MockerFixture
) -> None:
    # Polaris returned a non 404 error state and there is a retailer specific template
    retailer_slug = "test-retailer"
    reward_id = str(uuid4())
    retailer_error_template = """
    No reward for you, but here's a potato.
    """

    responses.get(f"{POLARIS_BASE_URL}/{retailer_slug}/reward/{reward_id}", json={}, status=500)
    mock_template_loader = mocker.patch("aquila.polaris_request.template_loader")
    mock_template_loader.get_template.return_value = retailer_error_template

    resp = test_client.get(url_for("rewards.reward", retailer=retailer_slug, reward=reward_id))
    assert resp.text == retailer_error_template
