import json
import pickle
from dataclasses import dataclass
from functools import wraps
from hashlib import md5
from pathlib import Path

from openai import AsyncClient

from genai_utils.day1.prompts import _Prompt

MEMOIZATION_DIR = (Path.home() / ".gen-ai-cache").resolve()

_UNSERIALIZABLE = "<unserializable>"


@dataclass
class _CacheConfig:
    enabled: bool
    show_cache_hit: bool = False

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True


cache_config = _CacheConfig(enabled=True, show_cache_hit=False)


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, _Prompt):
            return str(obj)
        if isinstance(obj, AsyncClient):
            return _UNSERIALIZABLE
        # TODO: add as many 'if' as necessary,
        # depending on the expected kwargs value types
        return super().default(obj)


def memoize(user_friendly_id=None, exclude_args_from_caching=()):
    def _memoize(func):
        @wraps(func)
        async def wrapper(**kwargs):
            if cache_config.enabled:
                nonlocal user_friendly_id
                try:
                    user_friendly_id = (
                        user_friendly_id
                        or f"{func.__module__}.{func.__qualname__}"
                    )
                except AttributeError:
                    user_friendly_id = "gen-ai-cache"

                caching_kwargs = {
                    k: v
                    for k, v in kwargs.items()
                    if k not in exclude_args_from_caching
                }

                cache_file = get_memoization_path(
                    user_friendly_id, caching_kwargs
                )
                if cache_file.exists():
                    if cache_config.show_cache_hit:
                        print("🟢 cache hit")
                    return pickle.loads(cache_file.read_bytes())

                if cache_config.show_cache_hit:
                    print("🔴 cache miss")

                result = await func(**kwargs)
                cache_file.write_bytes(pickle.dumps(result))
                return result
            else:
                return await func(**kwargs)

        return wrapper

    return _memoize


def get_memoization_path(user_friendly_id: str, /, kwargs):
    call_id = json.dumps(kwargs, sort_keys=True, cls=CustomJsonEncoder)

    call_hash = md5(call_id.encode("utf-8")).hexdigest()
    cache_file = f"{user_friendly_id}__{call_hash}"

    cache_dir = MEMOIZATION_DIR / user_friendly_id
    cache_dir.mkdir(exist_ok=True, parents=True)

    return cache_dir / cache_file
