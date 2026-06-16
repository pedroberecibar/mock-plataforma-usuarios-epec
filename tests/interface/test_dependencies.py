import pytest

from interface.dependencies import get_auth_provider


def test_get_auth_provider_is_an_unwired_placeholder() -> None:
    with pytest.raises(NotImplementedError):
        get_auth_provider()
