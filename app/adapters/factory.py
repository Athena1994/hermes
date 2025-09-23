from typing import Any, Callable, Dict

from app.adapters.base_adapter import BaseAdapter
from app.models import DataSource

# Registry maps `datasource type`->constructor(config_dict)->adapter
_REGISTRY: Dict[str, Callable[[Dict[str, Any]], Any]] = {}


def register_adapter(
    ds_type: str,
    ctor: Callable[[Dict[str, Any]], BaseAdapter],
) -> None:
    """Register an adapter constructor for a datasource type.

    ctor should accept a single argument: the datasource config dict, and
    return an adapter instance.
    """
    if ds_type in _REGISTRY:
        raise ValueError(
            f"Adapter already registered for datasource type '{ds_type}'")
    _REGISTRY[ds_type] = ctor


def get_adapter_for_datasource(ds: DataSource) -> BaseAdapter:
    """Return an adapter instance for a DataSource-like argument.

    If no registered adapter exists for the datasource type, raise a
    ValueError. The caller may choose to handle this and provide a
    fallback.
    """
    ctor = _REGISTRY.get(ds.type)
    if not ctor:
        raise ValueError(
            f"No adapter registered for datasource type '{ds.type}'")

    return ctor(ds.config)
