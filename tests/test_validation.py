import pytest

from hydra.domain.validation import normalize_url, validate_profile_name


def test_normalize_url_adds_https():
    assert normalize_url("example.com") == "https://example.com"


def test_invalid_scheme_is_rejected():
    with pytest.raises(ValueError):
        normalize_url("ftp://example.com")


def test_profile_name_is_restricted():
    assert validate_profile_name("conta_1") == "conta_1"
    with pytest.raises(ValueError):
        validate_profile_name("conta 1")
