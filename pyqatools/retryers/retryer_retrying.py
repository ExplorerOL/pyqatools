from __future__ import annotations

import time
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from typing import Callable, Iterator, Optional, TypeVar

from retrying import Retrying

# Предполагается, что RetryConfig импортируется или определен так:
from pyqatools.retryers.retryer_config import RetryConfig, RetryConfigs
from pyqatools.retryers.retryer_protocol import RetryerProtocol

T = TypeVar('T')


class RetryerRetrying(RetryerProtocol):
    """Центральный retry-механизм на базе retrying (sync only)."""

    _retry_config: ContextVar[Optional[RetryConfig]] = ContextVar('retry_config', default=None)

    def __init__(self, config: RetryConfig = RetryConfigs.T30000_I1000.value):
        self._config = config
        self._success = False

    def __iter__(self) -> Iterator['_RetryBlock']:
        """Iterator for block-style retry."""
        start_time = time.perf_counter()
        attempts_done = 0

        while not self._success:
            if self._config.attempts is not None and attempts_done >= self._config.attempts:
                break

            if self._config.timeout_ms is not None:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                if elapsed_ms >= self._config.timeout_ms:
                    break

            yield _RetryBlock(self, start_time, attempt_number=attempts_done + 1)
            attempts_done += 1

    @classmethod
    def _get_config(cls) -> Optional[RetryConfig]:
        return cls._retry_config.get()

    @classmethod
    def _set_config(cls, config: RetryConfig):
        return cls._retry_config.set(config)

    @classmethod
    def _reset_config(cls, token):
        cls._retry_config.reset(token)

    @staticmethod
    def retry(
        config: Optional[RetryConfig] = RetryConfigs.T30000_I1000.value,
    ) -> Callable[[Callable[..., T]], Callable[..., T]]:
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            def wrapper(*args, **kwargs) -> T:
                ctx_config = RetryerRetrying._get_config()
                active_config = ctx_config or config

                if active_config is None:
                    return func(*args, **kwargs)

                # Используем библиотеку retrying
                retrying_obj = Retrying(
                    stop_max_attempt_number=active_config.attempts,
                    stop_max_delay=active_config.timeout_ms,
                    wait_fixed=active_config.interval_ms,
                    retry_on_exception=lambda exc: isinstance(exc, active_config.retry_exception),
                    wrap_exception=False,
                )
                return retrying_obj.call(func, *args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    @contextmanager
    def with_config(config: RetryConfig):
        current = RetryerRetrying._get_config()
        active_config = config or current
        token = RetryerRetrying._set_config(active_config)
        try:
            yield
        finally:
            RetryerRetrying._reset_config(token)


class _RetryBlock:
    def __init__(self, parent: RetryerRetrying, start_time: float, attempt_number: int):
        self._parent = parent
        self._config = parent._config
        self._start_time = start_time
        self.attempt_number = attempt_number

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value is None:
            self._parent._success = True
            return False

        if not isinstance(exc_value, self._config.retry_exception):
            return False

        if self._config.timeout_ms is not None:
            elapsed_ms = (time.perf_counter() - self._start_time) * 1000
            if elapsed_ms >= self._config.timeout_ms:
                return False

        time.sleep(self._config.interval_ms / 1000)

        return True
