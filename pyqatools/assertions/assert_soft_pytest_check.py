from functools import wraps

from pytest_check import check as assert_soft_pytest_check


def assert_soft_for_method(func):
    __tracebackhide__ = True

    @wraps(func)
    def wrapper(*args, **kwargs):
        with assert_soft_pytest_check:
            return func(*args, **kwargs)

    return wrapper


assert_soft_pytest_check.assert_soft_for_method = assert_soft_for_method
