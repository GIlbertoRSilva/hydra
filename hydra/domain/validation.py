from __future__ import annotations

from urllib.parse import urlparse

from hydra.config import LAYOUTS


def normalize_url(value: str) -> str:
    value = value.strip()
    if not value:
        return "about:blank"
    if "://" not in value and not value.startswith("about:"):
        value = f"https://{value}"
    scheme = urlparse(value).scheme.lower()
    if scheme not in {"http", "https", "about"}:
        raise ValueError("A URL deve usar http, https ou about:.")
    return value


def validate_profile_name(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    allowed = all(char.isalnum() or char in "._-" for char in value)
    if not allowed or len(value) > 64:
        raise ValueError("O perfil deve usar apenas letras, números, ponto, hífen ou sublinhado.")
    return value


def validate_layout(value: str) -> str:
    if value not in LAYOUTS:
        raise ValueError("Layout inválido.")
    return value
