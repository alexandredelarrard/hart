from collections.abc import Mapping
from copy import deepcopy
from functools import reduce
from typing import Any, Optional


def deepmerge(*sources: Mapping, destination: Optional[dict] = None) -> dict:
    """Merge all `sources` mappings into a single `destination` mapping."""
    destination = {} if destination is None else destination.copy()
    return reduce(_do_merge, sources, destination)


def _do_merge(destination: dict, source: dict) -> dict:
    # inplace mutation is acceptable in this scoped, private function.
    for key, value in source.items():
        if key in destination and _is_recursive_merge(destination[key], value):
            _do_merge(destination[key], value)
            continue
        destination[key] = deepcopy(source[key])

    return destination


def _is_recursive_merge(x: Any, y: Any) -> bool:
    return isinstance(x, Mapping) and isinstance(y, Mapping)
