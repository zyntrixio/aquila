from collections.abc import Generator

import pytest

from pytest_mock import MockerFixture
from werkzeug.exceptions import HTTPException

from aquila import check_metrics_port, create_app


@pytest.fixture
def request_context() -> Generator[None, None, None]:
    app = create_app()
    with app.test_request_context():
        yield


def test_check_metrics_port_no_metrics_debug(request_context: None, mocker: MockerFixture) -> None:
    mocker.patch("aquila.METRICS_DEBUG", False)
    mock_request = mocker.patch("aquila.request")
    mock_request.server = ("localhost", 9100)
    mock_request.path = "/metrics"

    try:
        check_metrics_port()
    except HTTPException:
        pytest.fail("Raised an unexpected exception.")

    mock_request.server = ("localhost", 9000)
    mock_request.path = "/metrics"

    with pytest.raises(HTTPException) as ex:
        check_metrics_port()

    assert ex.typename == "NotFound"

    mock_request.server = ("localhost", 9100)
    mock_request.path = "/readyz"

    with pytest.raises(HTTPException) as ex:
        check_metrics_port()

    assert ex.typename == "NotFound"


def test_check_metrics_port_metrics_debug(request_context: None, mocker: MockerFixture) -> None:
    mocker.patch("aquila.METRICS_DEBUG", True)
    mock_request = mocker.patch("aquila.request")

    mock_request.server = ("localhost", 9100)
    mock_request.path = "/metrics"

    try:
        check_metrics_port()
    except HTTPException:
        pytest.fail("Raised an unexpected exception.")

    mock_request.server = ("localhost", 9100)
    mock_request.path = "/readyz"

    with pytest.raises(HTTPException) as ex:
        check_metrics_port()

    assert ex.typename == "NotFound"

    mock_request.server = ("localhost", 9000)
    mock_request.path = "/metrics"

    try:
        check_metrics_port()
    except HTTPException:
        pytest.fail("Raised an unexpected exception.")

    assert ex.typename == "NotFound"
