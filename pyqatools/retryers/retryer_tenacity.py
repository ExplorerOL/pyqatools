from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from typing import Callable, Generator, Optional, TypeVar

from tenacity import (
    AttemptManager,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    stop_after_delay,
    wait_fixed,
)

from pyqatools.retryers.retryer_config import RetryConfig, RetryConfigs
from pyqatools.retryers.retryer_protocol import RetryerProtocol

T = TypeVar('T')


class RetryerTenacity(RetryerProtocol):
    _retry_config: ContextVar[Optional[RetryConfig]] = ContextVar('retry_config', default=None)

    def __init__(self, config: RetryConfig = RetryConfigs.T30000_I1000.value):
        self._config = config
        stop = (
            stop_after_attempt(self._config.attempts)
            if self._config.attempts
            else stop_after_delay(self._config.timeout_ms / 1000)
        )
        self._retrying = Retrying(
            stop=stop,
            wait=wait_fixed(config.interval_ms / 1000),
            retry=retry_if_exception_type(config.retry_exception),
            reraise=True,
        )

    def __iter__(self) -> Generator[AttemptManager, None, None]:
        """Iterator for block-style retry."""
        yield from self._retrying

    @classmethod
    def _get_config(cls) -> RetryConfig | None:
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
                ctx_config = RetryerTenacity._get_config()
                active_config = ctx_config or config

                if active_config is None:
                    return func(*args, **kwargs)
                stop = (
                    stop_after_attempt(active_config.attempts)
                    if active_config.attempts
                    else stop_after_delay(active_config.timeout_ms / 1000)
                )
                retrying = Retrying(
                    stop=stop,
                    wait=wait_fixed(active_config.interval_ms / 1000),
                    retry=retry_if_exception_type(active_config.retry_exception),
                    reraise=True,
                )
                return retrying(func, *args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    @contextmanager
    def with_config(config: RetryConfig):
        current = RetryerTenacity._get_config()
        active_config = config or current

        token = RetryerTenacity._set_config(active_config)
        try:
            yield
        finally:
            RetryerTenacity._reset_config(token)
