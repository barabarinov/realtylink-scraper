from functools import wraps

from selenium.common.exceptions import NoSuchElementException


def handle_exception(
    default_value: str | int,
    exception: Exception = NoSuchElementException,
) -> callable:
    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception as e:
                print(f"Element not found:({e})")
                return default_value

        return wrapper

    return deco
