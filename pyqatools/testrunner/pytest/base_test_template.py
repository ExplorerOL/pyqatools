from typing import Callable

from pyqatools.assertions.assert_step import assert_step
from pyqatools.config.config_pyqatools import config_pyqatools


class BaseTestTemplate:
    """Шаблон базового тестового класса."""

    logger = config_pyqatools.logger
    reporter = config_pyqatools.reporter
    assert_step: Callable = assert_step
    # def __enter__(self) -> None:
    #     assert_soft_pytest_check.__enter__()
    #     self.assert_reporter_step.__enter__()

    # def __exit__(self, exc_type, exc_val, exc_tb) -> bool | None:
    #     self.assert_reporter_step.__exit__(exc_type, exc_val, exc_tb)
    #     assert_soft_pytest_check.__exit__(exc_type, exc_val, exc_tb)
    #     return True

    def ARRANGE(self, msg: str = ''):  # noqa: N802
        section_name = f'ARRANGE: {msg}'
        if self.logger:
            self.logger.info(msg=section_name)
        if self.reporter:
            return self.reporter.step(name=section_name)

    def ACT(self, msg: str = ''):  # noqa: N802
        section_name = f'ACT: {msg}'
        if self.logger:
            self.logger.info(msg=section_name)
        if self.reporter:
            return self.reporter.step(name=section_name)

    def ASSERT(self, msg: str = '', soft: bool = True):  # noqa: N802
        section_name = f'ASSERT: {msg}'
        return assert_step(msg=f'{section_name}', soft=soft)
