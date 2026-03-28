from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components

_FRONTEND_DIR = Path(__file__).parent / "frontend" / "dist"

_component_func = components.declare_component(
    "yelp_tsx_component",
    path=str(_FRONTEND_DIR),
)


def yelp_tsx_component(
    *,
    key: str | None = None,
    default: Any = None,
    **kwargs: Any,
) -> Any:
    return _component_func(
        key=key,
        default=default,
        **kwargs,
    )


__all__ = ["yelp_tsx_component"]
