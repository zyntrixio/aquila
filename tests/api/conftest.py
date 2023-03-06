from collections.abc import Generator
from typing import TYPE_CHECKING

import pytest

from aquila import create_app

if TYPE_CHECKING:
    from flask.testing import FlaskClient


@pytest.fixture(scope="function")
def test_client() -> Generator["FlaskClient", None, None]:
    app = create_app()
    with app.app_context(), app.test_request_context():
        yield app.test_client()
