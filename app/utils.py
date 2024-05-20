from functools import wraps

from selenium.common.exceptions import NoSuchElementException


def handle_no_such_element_exception(value: str | int):
    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except NoSuchElementException as e:
                print(f"Element not found:({e})")
                return value

        return wrapper

    return deco
