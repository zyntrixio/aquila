from typing import TYPE_CHECKING
from uuid import uuid4

import responses

from flask import render_template, url_for
from pytest_mock import MockerFixture

from aquila.settings import COSMOS_BASE_URL, POLARIS_BASE_URL

if TYPE_CHECKING:
    from flask.testing import FlaskClient


REQUEST_MAPPER = {
    COSMOS_BASE_URL: "/r",
    POLARIS_BASE_URL: "/reward",
}


@responses.activate
def test_reward_ok(test_client: "FlaskClient", mocker: MockerFixture) -> None:
    """
    This tests fetching reward from both POLARIS_BASE_URL and COSMOS_BASE_URL.

    The request destination for fetching the rewards is determined by the request
    path.

    /r -> COSMOS_BASE_URL
    /reward -> POLARIS_BASE_URL
    """

    code = "TSTRWDCODE1234"
    expiry_date = "1999-12-31"
    pin = "1234"

    template = """
    <p>{{ code }}</p>
    <p>{{ expiry_date }}</p>
    <p>{{ pin }}</p>
    """
    expected_response = f"""
    <p>{ code }</p>
    <p>31/12/1999</p>
    <p>{ pin }</p>
    """

    retailer_slug = "test-retailer"
    template_slug = "test-template"
    reward_id = str(uuid4())

    for base_url, endpoint_path in REQUEST_MAPPER.items():
        mock_metric = mocker.patch("aquila.endpoints.rewards.reward_requests_total")

        responses.get(
            f"{base_url}/{retailer_slug}/reward/{reward_id}",
            json={
                "code": code,
                "expiry_date": expiry_date,
                "template_slug": template_slug,
                "pin": pin,
            },
        )
        mock_template_loader = mocker.patch("aquila.endpoints.rewards.template_loader")
        mock_template_loader.get_template.return_value = template
        resp = test_client.get(f"{endpoint_path}?retailer={retailer_slug}&reward={reward_id}")
        assert resp.text == expected_response

        mock_metric.labels.assert_called_once_with(
            retailer_slug=retailer_slug, response_status=200, response_template=template_slug
        )


@responses.activate
def test_reward_fallback_template(test_client: "FlaskClient", mocker: MockerFixture) -> None:
    mock_metric = mocker.patch("aquila.endpoints.rewards.reward_requests_total")

    code = "TSTRWDCODE1234"
    expiry_date = "1999-12-31"
    pin = "1234"

    expected_response = render_template("default.html", code=code, expiry_date="31/12/1999", pin=pin)

    retailer_slug = "test-retailer"
    reward_id = str(uuid4())

    for base_url, endpoint_path in REQUEST_MAPPER.items():
        mock_metric = mocker.patch("aquila.endpoints.rewards.reward_requests_total")

        responses.get(
            f"{base_url}/{retailer_slug}/reward/{reward_id}",
            json={
                "code": code,
                "expiry_date": expiry_date,
                "template_slug": "test-template",
                "pin": pin,
            },
        )
        mock_template_loader = mocker.patch("aquila.endpoints.rewards.template_loader")
        mock_template_loader.get_template.return_value = None
        resp = test_client.get(f"{endpoint_path}?retailer={retailer_slug}&reward={reward_id}")
        assert resp.text == expected_response
        mock_metric.labels.assert_called_once_with(
            retailer_slug=retailer_slug, response_status=200, response_template="default"
        )


def test_reward_missing_param(test_client: "FlaskClient", mocker: MockerFixture) -> None:
    for endpoint_path in REQUEST_MAPPER.values():
        mock_metric = mocker.patch("aquila.endpoints.rewards.reward_requests_total")

        resp = test_client.get(f"{endpoint_path}?reward=stuff")
        assert resp.status_code == 400
        mock_metric.labels.assert_called_with(retailer_slug="N/A", response_status=400, response_template="N/A")

        resp = test_client.get(f"{endpoint_path}?retailer=stuff")
        assert resp.status_code == 400
        mock_metric.labels.assert_called_with(retailer_slug="stuff", response_status=400, response_template="N/A")

        resp = test_client.get(endpoint_path)
        assert resp.status_code == 400
        mock_metric.labels.assert_called_with(retailer_slug="N/A", response_status=400, response_template="N/A")


@responses.activate
def test_reward_negative_responses(test_client: "FlaskClient", mocker: MockerFixture) -> None:
    expected_response = render_template("default_error.html")

    retailer_slug = "test-retailer"
    reward_id = str(uuid4())

    for base_url, endpoint_path in REQUEST_MAPPER.items():
        mock_metric = mocker.patch("aquila.fetch_reward.reward_requests_total")

        # Polaris / Cosmos returned a 404
        responses.get(f"{base_url}/{retailer_slug}/reward/{reward_id}", json={}, status=404)

        resp = test_client.get(f"{endpoint_path}?retailer={retailer_slug}&reward={reward_id}")
        assert resp.status_code == 404
        mock_metric.labels.assert_called_with(retailer_slug=retailer_slug, response_status=404, response_template="N/A")

        # Polaris / Cosmos  returned a non 404 error state
        responses.get(f"{base_url}/{retailer_slug}/reward/{reward_id}", json={}, status=500)

        resp = test_client.get(f"{endpoint_path}?retailer={retailer_slug}&reward={reward_id}")
        assert resp.text == expected_response
        mock_metric.labels.assert_called_with(
            retailer_slug=retailer_slug, response_status=200, response_template="default_error"
        )

        # an exception happened while trying to contact Polaris / Cosmos
        mock_requests = mocker.patch("aquila.fetch_reward.reward_requests_total")
        mock_requests.get.side_effect = Exception("random stuff happened")

        resp = test_client.get(f"{endpoint_path}?retailer={retailer_slug}&reward={reward_id}")
        assert resp.text == expected_response
        mock_metric.labels.assert_called_with(
            retailer_slug=retailer_slug, response_status=200, response_template="default_error"
        )


@responses.activate
def test_reward_negative_response_retailer_error_template(test_client: "FlaskClient", mocker: MockerFixture) -> None:
    # Polaris / Cosmos returned a non 404 error state and there is a retailer specific template
    retailer_slug = "test-retailer"
    reward_id = str(uuid4())
    retailer_error_template = """
    No reward for you, but here's a potato.
    """

    for base_url, endpoint_path in REQUEST_MAPPER.items():
        mock_metric = mocker.patch("aquila.fetch_reward.reward_requests_total")

        responses.get(f"{base_url}/{retailer_slug}/reward/{reward_id}", json={}, status=500)
        mock_template_loader = mocker.patch("aquila.fetch_reward.template_loader")
        mock_template_loader.get_template.return_value = retailer_error_template

        resp = test_client.get(f"{endpoint_path}?retailer={retailer_slug}&reward={reward_id}")
        assert resp.text == retailer_error_template

        mock_metric.labels.assert_called_with(
            retailer_slug=retailer_slug, response_status=200, response_template="error"
        )


def test_metrics_ok(test_client: "FlaskClient", mocker: MockerFixture) -> None:
    mocker.patch("aquila.METRICS_DEBUG", True)
    mocker.patch("aquila.endpoints.metrics.PROMETHEUS_MULTIPROC_DIR", None)
    resp = test_client.get(url_for("metrics.metrics"))
    assert resp.status_code == 200
    assert "# HELP python_gc_objects_collected_total" in resp.text
