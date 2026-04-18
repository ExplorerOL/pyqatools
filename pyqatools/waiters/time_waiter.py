import time

from pyqatools.exceptions.general_exceptions import EmptyValueError, UnexpectedValueError
from pyqatools.reporters.reporter_base_classes import (
    ClassWithStepLoggingAndReporting,
)


class TimeWaiter(ClassWithStepLoggingAndReporting):
    @staticmethod
    def wait(timeout_ms: int, msg: str) -> None:
        """Ожидание по времени."""
        if not msg:
            raise EmptyValueError('Waiter message must be not empty!')
        if timeout_ms < 0:
            raise UnexpectedValueError('Waiter timeout must be positive number!')
        timeout_s = timeout_ms / 1000
        time.sleep(timeout_s)
