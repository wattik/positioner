from typing import Callable


def collector(final_type: Callable = None):
    final_type = final_type or list

    def decorator(f):
        def wrapper(*args, **kwargs):
            return final_type(f(*args, **kwargs))

        return wrapper

    return decorator
