from pytest_mock import MockerFixture

from aquila.settings import check_testing


def test_check_testing(mocker: MockerFixture) -> None:
    mock_sys = mocker.patch("aquila.settings.sys")

    mock_sys.argv = ["pytest", "args"]
    assert check_testing(False)
    assert check_testing(True)

    mock_sys.argv = ["poetry", "run", "pytest", "args"]
    assert check_testing(False)
    assert check_testing(True)

    mock_sys.argv = ["other", "args"]
    assert check_testing(False) is False
    assert check_testing(True)
