"""
CREDITS: https://gist.github.com/dlebech/c16a34f735c0c4e9b604

The caching utility provides a single wrapper function that can be used to
provide a bit of extra speed for some often used function.

Usage::
    import cache
    @cache.memoize
    def myfun(x, y):
        return x + y
Also support asyncio coroutines::
    @cache.memoize
    async def myfun(x, y):
        x_result = await fetch_x(x)
        return x_result + y
The cache can be manually cleared with `myfun.cache.clear()`
"""
import asyncio
import inspect
from functools import wraps

__all__ = ["memoize"]


def _wrap_coroutine_storage(cache_dict, key, future):

    async def wrapper():
        val = await future
        cache_dict[key] = val
        return val

    return wrapper()


def _wrap_value_in_coroutine(val):

    async def wrapper():
        return val

    return wrapper()


def memoize(ignore_values: (set, None)):
    if not ignore_values:
        ignore_values = set()
    assert isinstance(ignore_values, set)

    def decorator(f):
        """
        An in-memory cache wrapper that can be used on any function,
         including coroutines.
        """
        __cache = {}

        @wraps(f)
        def wrapper(*args, **kwargs):
            call_args = inspect.getcallargs(f, *args, **kwargs)
            keys = [v for k, v in call_args.items() if k not in ignore_values]
            key = f"{f.__module__}#{f.__name__}#{repr(keys)}"
            try:
                val = __cache[key]
                if asyncio.iscoroutinefunction(f):
                    return _wrap_value_in_coroutine(val)

                return val

            except KeyError:
                val = f(*args, **kwargs)

                if asyncio.iscoroutine(val):
                    # If the value returned by the function is a coroutine, wrap
                    # the future in a new coroutine that stores the actual
                    # result in the cache.
                    return _wrap_coroutine_storage(__cache, key, val)

                # Otherwise just store and return the value directly
                __cache[key] = val
                return val

        return wrapper

    return decorator
