"""
Runtime shim to accommodate environments where pydantic 2 internals are unavailable.

Some dependencies import `pydantic._internal._signature`; when running in
environments with pydantic v1, we provide a lightweight stub so imports succeed.
"""

from __future__ import annotations

import sys
import types


def ensure_pydantic_internal_signature():
    if "pydantic._internal._signature" in sys.modules:
        return
    internal_mod = types.ModuleType("pydantic._internal")
    signature_mod = types.ModuleType("pydantic._internal._signature")
    dataclasses_mod = types.ModuleType("pydantic._internal._dataclasses")

    def _field_name_for_signature(field):
        return getattr(field, "name", None)

    def dataclass(cls=None, **kwargs):
        return cls

    dataclasses_mod.dataclass = dataclass
    dataclasses_mod.PydanticDataclassDefaults = type("PydanticDataclassDefaults", (), {})  # minimal placeholder
    signature_mod._field_name_for_signature = _field_name_for_signature
    sys.modules["pydantic._internal"] = internal_mod
    sys.modules["pydantic._internal._signature"] = signature_mod
    sys.modules["pydantic._internal._dataclasses"] = dataclasses_mod


def ensure_pydantic_public_shims():
    """
    Provide missing public symbols when running with older pydantic versions.
    """
    try:
        import pydantic  # type: ignore
    except Exception:
        return
    for name, fallback in {
        "Secret": str,
        "RootModel": object,
        "Json": object,
    }.items():
        if not hasattr(pydantic, name):
            setattr(pydantic, name, fallback)


ensure_pydantic_internal_signature()
