
from typing import Callable, TYPE_CHECKING, Any
from app.adapters.base_adapter import BaseAdapter

if TYPE_CHECKING:
    from app.models import DataSource


_REGISTRY: dict[str, Callable[[dict], BaseAdapter]] = {}


def register_adapter(name: str, cstr: Callable) -> None:
    if name in _REGISTRY:
        raise ValueError(
            f"Adapter already registered for datasource '{name}'")
    _REGISTRY[name] = cstr


def get_adapter_for_datasource(ds: Any) -> BaseAdapter:
    """Return an adapter instance for a DataSource-like argument.

    If no registered adapter exists for the datasource type, raise a
    ValueError. The caller may choose to handle this and provide a
    fallback.
    """
    # Accept any DataSource-like object (duck-typing) to avoid importing
    # Django models at module import time.
    name = getattr(ds, 'name', None) or getattr(ds, 'type', None)
    ctor = _REGISTRY.get(name)
    if not ctor:
        raise ValueError(
            f"No adapter registered for datasource '{name}'")

    return ctor(ds.config)
