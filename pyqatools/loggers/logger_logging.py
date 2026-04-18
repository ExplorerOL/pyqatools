"""Модуль логгера."""

import inspect
import logging
import os
import shutil
from functools import wraps
from importlib import reload
from pathlib import Path
from typing import Any, Callable, Generator, ParamSpec, TypeVar

from pyqatools.config.config_pyqatools import LoggerProtocol
from pyqatools.loggers.log_levels import LogLevels

PT = ParamSpec('PT')  # param type
YT = TypeVar('YT')  # yield type
ST = TypeVar('ST')  # send type
RT = TypeVar('RT')  # return type


class XdistWorkerIdFilter(logging.Filter):
    """Фильтр для добавления идентификатора xdist worker в логи."""

    def __init__(self, worker_id: str):
        super().__init__()
        self.__worker_id = worker_id

    def filter(self, record):
        record.worker_id = self.__worker_id
        return True


class LoggerLogging(LoggerProtocol):
    """Класс логгера для тестрана."""

    LOGGER_NAME = 'LOGGER_LOGGING'
    LOG_FILE_FORMAT = '%(asctime)s | %(levelname)s | %(filename)s:%(lineno)s - %(message)s \n'

    __msg_prefix_step = 'Step: '
    __msg_prefix_static_step = 'Static Step: '
    __msg_prefix_method = 'Method: '
    __msg_prefix_static_method = 'Static Method: '
    __msg_prefix_fixture = 'Fixture: '

    def __init__(
        self,
        log_file_path: Path,
        log_level: LogLevels = LogLevels.DEBUG,
        clear_handlers: bool = False,
        console_output: bool = True,
        file_output: bool = True,
    ):
        self.__log_levels = LogLevels
        self.__worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'master')
        log_file_path = log_file_path.with_stem(log_file_path.stem + f'_{self.__worker_id}')

        self.__log_file_path = log_file_path
        self._add_custom_log_levels()
        self._clear_reports_dir()

        self.__logger = logging.getLogger(self.LOGGER_NAME)
        self.__logger.setLevel(log_level.value)

        if clear_handlers:
            if self.__logger.hasHandlers():
                self.__logger.handlers.clear()

        formatter = logging.Formatter(
            fmt='%(asctime)s.%(msecs)03d | [%(worker_id)s] | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        console_formatter = logging.Formatter(
            fmt='%(asctime)s %(msecs)03d | [%(worker_id)s] | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        # Создаем файловый handler
        if file_output:
            file_handler = logging.FileHandler(log_file_path, mode='w', encoding='utf-8')
            file_handler.setLevel(log_level.value)
            file_handler.setFormatter(formatter)
            self.__logger.addHandler(file_handler)

        # Добавляем консольный handler если requested
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(console_formatter)
            console_handler.setLevel(log_level.value)
            self.__logger.addHandler(console_handler)

        self.__logger.propagate = False

        self.__logger.addFilter(XdistWorkerIdFilter(worker_id=self.__worker_id))

        self.info(f'Логгирование с уровнем {log_level} начато с помощью логгера {self.LOGGER_NAME}')

    def _add_custom_log_levels(self) -> None:
        """Добавление пользовательских уровней логгирования."""
        for log_level in self.__log_levels:
            if log_level.name not in logging._nameToLevel.keys():
                logging.addLevelName(log_level.value, log_level.name)

    def _clear_reports_dir(self) -> None:
        """Очистка директории с отчетами.

        В многопоточном режиме очистку выполняет только master-процесс.
        В однопоточном режиме очистка выполняется всегда.

        Args:
            reports_dir: Путь к директории с отчетами
        """
        # Получаем идентификатор worker из переменных окружения
        # worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'master')

        # Очищаем только из master-процесса
        if self.__worker_id == 'master':
            reports_dir = self.__log_file_path.parent.absolute()
            if reports_dir.exists() and reports_dir.is_dir():
                shutil.rmtree(reports_dir)
            reports_dir.mkdir(parents=True, exist_ok=True)

    def set_log_level(self, log_level: str) -> None:
        """Установка уровня логгирования."""
        self.remove_logger()
        if log_level not in list(self.__log_levels.__members__.keys()):
            raise ValueError(f'Указанный уровень логгирования {log_level} не существует')

        logging.basicConfig(
            level=self.__log_levels[log_level].value,
            encoding='utf-8',
            filename=self.__log_file_path,
            filemode='w',
            format=self.LOG_FILE_FORMAT,
        )
        self.__logger = logging.getLogger(self.LOGGER_NAME)
        self.__logger.debug(f'Уровень логгирования изменен на {log_level}')

    def remove_logger(self) -> None:
        """Удаление логгера."""
        self.__logger.info(f'Удаление логгера {self.LOGGER_NAME}')
        logging.shutdown()
        reload(logging)
        self._add_custom_log_levels()

    def configure_msg_prefixes(
        self,
        msg_prefix_step: str | None = None,
        msg_prefix_static_step: str | None = None,
        msg_prefix_method: str | None = None,
        msg_prefix_static_method: str | None = None,
        msg_prefix_static_fixture: str | None = None,
    ) -> None:
        if msg_prefix_step is not None:
            self.__msg_prefix_step = msg_prefix_step
        if msg_prefix_static_step is not None:
            self.__msg_prefix_static_step = msg_prefix_static_step
        if msg_prefix_method is not None:
            self.__msg_prefix_method = msg_prefix_method
        if msg_prefix_static_method is not None:
            self.__msg_prefix_static_method = msg_prefix_static_method
        if msg_prefix_static_fixture is not None:
            self.__msg_prefix_fixture = msg_prefix_static_method

    def deep_trace(self, msg: Any) -> None:
        """Вывод в лог информации с уровнем DEEP_TRACE."""
        if self.__logger.isEnabledFor(self.__log_levels.DEEP_TRACE.value):
            self.__logger.log(self.__log_levels.DEEP_TRACE.value, str(msg))

    def trace(self, msg: Any) -> None:
        """Вывод в лог информации с уровнем TRACE."""
        if self.__logger.isEnabledFor(self.__log_levels.TRACE.value):
            self.__logger.log(self.__log_levels.TRACE.value, str(msg))

    def debug(self, msg: Any) -> None:
        """Вывод в лог информации с уровнем DEBUG."""
        if self.__logger.isEnabledFor(self.__log_levels.DEBUG.value):
            self.__logger.debug(str(msg))

    def info(self, msg: Any) -> None:
        """Вывод в лог информации с уровнем INFO."""
        if self.__logger.isEnabledFor(self.__log_levels.INFO.value):
            self.__logger.info(str(msg))

    def step(self, msg: Any) -> None:
        """Вывод в лог информации с уровнем STEP."""
        if self.__logger.isEnabledFor(self.__log_levels.STEP.value):
            self.__logger.log(self.__log_levels.STEP.value, str(msg))

    def fixture(self, msg: Any) -> None:
        """Вывод в лог информации с уровнем FIXTURE."""
        if self.__logger.isEnabledFor(self.__log_levels.FIXTURE.value):
            self.__logger.log(self.__log_levels.FIXTURE.value, str(msg))

    def test(self, msg: Any) -> None:
        """Вывод в лог информации с уровнем TEST."""
        if self.__logger.isEnabledFor(self.__log_levels.TEST.value):
            self.__logger.log(self.__log_levels.TEST.value, str(msg))

    def success(self, msg: Any) -> None:
        """Вывод в лог информации с уровнем SUCCESS."""
        if self.__logger.isEnabledFor(self.__log_levels.SUCCESS.value):
            self.__logger.log(self.__log_levels.SUCCESS.value, str(msg))

    def warning(self, msg: Any) -> None:
        """Вывод в лог информации с уровнем WARNING."""
        self.__logger.warning(str(msg))

    def error(self, msg: Any) -> None:
        """Вывод в лог информации с уровнем ERROR."""
        self.__logger.error(str(msg))

    def log_fixture(self, func: Callable[PT, RT] | Generator[YT, ST, RT]) -> Callable[PT, RT] | Generator[YT, ST, RT]:
        """Логгирование фикстуры."""

        # Для логирования фикстуры-генератора сделана специальная обертка, иначе фикстура не выполняется
        first_line_from_docstring = str(func.__doc__).split('\n')[0] if func.__doc__ else ''

        @wraps(func)  # type: ignore
        def func_wrapper(*args, **kwargs):
            __tracebackhide__ = True
            self.fixture(
                f'{self.__msg_prefix_fixture}{first_line_from_docstring} | {func.__module__}::{func.__qualname__}',
            )
            if args or kwargs:
                self.debug(f'Args {func.__qualname__}: args={repr(args[1:])}, kwargs={repr(kwargs)}')
            result = func(*args, **kwargs)  # type: ignore
            if result is not None:
                self.debug(f'Result {func.__qualname__}: {result!r}')
            return result

        @wraps(func)  # type: ignore
        def gen_wrapper(*args, **kwargs):
            __tracebackhide__ = True
            self.fixture(
                f'{self.__msg_prefix_fixture}(setup): {first_line_from_docstring} | {func.__module__}::{func.__qualname__}',  # noqa E501
            )
            if args or kwargs:
                self.debug(f'Args {func.__qualname__}: args={repr(args[1:])}, kwargs={repr(kwargs)}')
            for result in func(*args, **kwargs):  # type: ignore
                if result is not None:
                    self.debug(f'Result {func.__qualname__}: {result!r}')
                yield result
            self.fixture(
                f'{self.__msg_prefix_fixture}(teardown): {first_line_from_docstring} | {func.__module__}::{func.__qualname__}',  # noqa E501
            )

        return gen_wrapper if inspect.isgeneratorfunction(func) else func_wrapper

    def log_step(self, func: Callable[PT, RT]) -> Callable[PT, RT]:
        """Логгирование шага."""
        __tracebackhide__ = True

        @wraps(func)
        def wrapper(*args, **kwargs):
            __tracebackhide__ = True
            step_self = args[0]
            first_line_from_docstring = str(func.__doc__).split('\n')[0] if func.__doc__ else ''
            self.step(
                f'{self.__msg_prefix_step}{first_line_from_docstring} | {step_self.__module__} ->'
                f'{step_self.__class__.__name__} -> {func.__name__}'
            )
            if args[1:] or kwargs:
                self.debug(f'Args {func.__name__}: args={repr(args[1:])}, kwargs={repr(kwargs)}')
            result = func(*args, **kwargs)
            if result is not None:
                self.debug(f'Result: {func.__name__}: {result!r}')
            return result

        return wrapper

    def log_method(self, func: Callable[PT, RT]) -> Callable[PT, RT]:
        """Логгирование метода."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            __tracebackhide__ = True
            method_self = args[0]
            first_line_from_docstring = str(func.__doc__).split('\n')[0] if func.__doc__ else ''
            self.debug(
                f'{self.__msg_prefix_method}{first_line_from_docstring} | {method_self.__module__} -> {method_self.__class__.__name__} -> {func.__name__}',  # noqa E501
            )
            if args[1:] or kwargs:
                self.trace(f'Args {func.__name__}: args={repr(args[1:])}, kwargs={repr(kwargs)}')
            result = func(*args, **kwargs)
            if result is not None:
                self.trace(f'Result: {func.__name__}: {result!r}')
            return result

        return wrapper

    def log_static_method(self, func: Callable[PT, RT]) -> Callable[PT, RT]:
        """Логгирование статического метода."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            __tracebackhide__ = True
            first_line_from_docstring = str(func.__doc__).split('\n')[0] if func.__doc__ else ''
            self.trace(
                f'{self.__msg_prefix_static_method}{first_line_from_docstring} | {func.__module__} -> {func.__class__.__name__} -> {func.__name__}',  # noqa E501
            )
            if args or kwargs:
                self.debug(f'Args {func.__name__}: args={repr(args[1:])}, kwargs={repr(kwargs)}')
            result = func(*args, **kwargs)
            return result

        return wrapper

    def log_static_step(self, func: Callable[PT, RT]) -> Callable[PT, RT]:
        """Логгирование статического шага."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            __tracebackhide__ = True
            first_line_from_docstring = str(func.__doc__).split('\n')[0] if func.__doc__ else ''

            self.step(
                f'{self.__msg_prefix_static_step}{first_line_from_docstring} | {func.__module__} -> {func.__class__.__name__} -> {func.__name__} | {first_line_from_docstring}'  # noqa E501
            )
            if args or kwargs:
                self.debug(f'Args {func.__name__}: {repr(args)} {repr(kwargs)}')
            result = func(*args, **kwargs)
            if result is not None:
                self.debug(f'Result: {func.__name__}: {result!r}')
            return result

        return wrapper
