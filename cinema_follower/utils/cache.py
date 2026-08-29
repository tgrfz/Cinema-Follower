import json
from functools import wraps

from cinema_follower.db import redis_client

REDIS_TTL_TIME = 24 * 60 * 60


def cache_result_set(key_template, ttl=REDIS_TTL_TIME):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            kwargs.update(zip(func.__code__.co_varnames, args))
            cache_key = key_template.format(**kwargs)

            cached = redis_client.smembers(cache_key)
            if cached:
                return cached

            result = func(**kwargs)
            redis_client.sadd(cache_key, *result)
            redis_client.expire(cache_key, ttl)
            return result
        return wrapper
    return decorator


def cache_result_json(key_template, ttl=REDIS_TTL_TIME):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            kwargs.update(zip(func.__code__.co_varnames, args))
            cache_key = key_template.format(**kwargs)

            result = redis_client.get(cache_key)
            if result:
                return json.loads(result)

            result = func(**kwargs)
            redis_client.set(cache_key, json.dumps(result), ex=ttl)
            return result
        return wrapper
    return decorator
