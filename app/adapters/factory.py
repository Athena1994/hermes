from typing import Any, Callable, Dict, Optional, Union

# Simple registry-based factory for adapters
# Registry maps datasource type string -> constructor(config_dict) -> adapter instance
_REGISTRY: Dict[str, Callable[[Dict[str, Any]], Any]] = {}


def register_adapter(ds_type: str, ctor: Callable[[Dict[str, Any]], Any]) -> None:
    """Register an adapter constructor for a datasource type.

    ctor should accept a single argument: the datasource config dict, and return
    an adapter instance.
    """
    _REGISTRY[ds_type] = ctor


def get_adapter_for_datasource(datasource: Union[Dict[str, Any], Any]) -> Any:
    """Return an adapter instance for a DataSource-like argument.

    datasource may be a Django model with .type and .config attributes or a plain dict.
    If no registered adapter exists for the datasource type, a minimal WebAdapter
    placeholder is returned which raises NotImplementedError on fetch operations.
    """
    ds_type = getattr(datasource, 'type', None) or (datasource.get('type') if isinstance(datasource, dict) else None)
    config = getattr(datasource, 'config', None) or (datasource.get('config') if isinstance(datasource, dict) else {})

    ctor = _REGISTRY.get(ds_type)
    if ctor:
        return ctor(config)

    raise ValueError(f"No adapter registered for datasource type '{ds_type}'")