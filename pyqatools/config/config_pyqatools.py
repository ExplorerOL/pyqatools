from dataclasses import dataclass
from typing import ContextManager

from pyqatools.loggers.logger_protocol import LoggerProtocol
from pyqatools.reporters.reporter_protocol import ReporterProtocol
from pyqatools.retryers.retryer_protocol import RetryerProtocol


@dataclass
class ConfigPyqatools:
    """Класс конфигурации ядра."""

    logger: LoggerProtocol | None = None
    reporter: ReporterProtocol | None = None
    assert_soft: ContextManager | None = None
    retryer: RetryerProtocol | None = None


config_pyqatools = ConfigPyqatools()
