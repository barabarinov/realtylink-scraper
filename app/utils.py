import logging
from functools import wraps

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def handle_exceptions(
    default_value: str | int,
    *exceptions,
) -> callable:
    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                logging.error(f"Exception occurred in {func.__name__}: {e}")
                return default_value

        return wrapper

    return deco
