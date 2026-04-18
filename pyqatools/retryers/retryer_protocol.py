from typing import (
    Callable,
    ContextManager,
    Iterator,
    Protocol,
    TypeVar,
)

from pyqatools.retryers.retryer_config import RetryConfig

T = TypeVar('T')


class RetryerProtocol(Protocol):
    def __iter__(self) -> Iterator:
        """For code block retrying."""
        ...

    @staticmethod
    def retry(
        config: RetryConfig | None = None,
    ) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """For decorator."""
        ...

    @staticmethod
    def with_config(config: RetryConfig) -> ContextManager[None]:
        """Context manager for redefine retryer settings."""
        ...
