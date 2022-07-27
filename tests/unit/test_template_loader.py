from pytest_mock import MockerFixture

from aquila.blob_storage import template_loader


def test_template_loader_no_fetch(mocker: MockerFixture) -> None:
    mock_logger = mocker.patch.object(template_loader, "logger")
    assert template_loader.dont_fetch_templates is True
    assert template_loader.get_template("any", "any") is None
    mock_logger.debug.assert_called_with("TESTING set to %s, returning None", True)
