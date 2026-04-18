from contextlib import contextmanager, nullcontext

from pyqatools.config.config_pyqatools import config_pyqatools

__tracebackhide__ = True


@contextmanager
def assert_step(msg: str = '', soft: bool = True):
    """Assert step with logging, reporting ans soft assert.

    Args:
        msg (str, optional): assert step name. Defaults to ''.
        soft (bool, optional): is soft assert. Defaults to True.

    """
    __tracebackhide__ = True
    if config_pyqatools.logger:
        config_pyqatools.logger.info(f'{msg}')
    with config_pyqatools.assert_soft if soft and config_pyqatools.assert_soft else nullcontext():
        with config_pyqatools.reporter.step(name=msg) if config_pyqatools.reporter else nullcontext():
            yield
