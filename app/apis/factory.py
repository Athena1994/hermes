


from typing import Callable

from app.apis.base_api_client import BaseApiClient


_REGISTRY: dict[str, Callable[[dict[str]], BaseApiClient]] = {}

def register_api(name: str, cstr: Callable) -> None:
    if name in _REGISTRY:
        raise ValueError(
            f"API client already registered for '{name}'")
    _REGISTRY[name] = cstr

def get(name: str, cfg: dict) -> BaseApiClient:
    """Return an API client instance for a registered name.

    If no registered client exists for the name, raise a ValueError.
    The caller may choose to handle this and provide a fallback.
    """
    ctor = _REGISTRY.get(name)
    if not ctor:
        raise ValueError(
            f"No API client registered for '{name}'")

    return ctor(cfg)

def list_registered() -> list[str]:
    """Return a list of registered API client names."""
    return list(_REGISTRY.keys())