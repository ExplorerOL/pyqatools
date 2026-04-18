import enum
from dataclasses import dataclass
from typing import Type


@dataclass(slots=True, frozen=True)
class RetryConfig:
    timeout_ms: int | None = 30000
    interval_ms: int = 500
    attempts: int | None = None
    retry_exception: Type[Exception] = Exception


class RetryConfigs(enum.Enum):
    T1000_I100 = RetryConfig(timeout_ms=1000, interval_ms=100)
    T2000_I500 = RetryConfig(timeout_ms=2000, interval_ms=500)
    T5000_I2000 = RetryConfig(timeout_ms=5000, interval_ms=2000)
    T30000_I1000 = RetryConfig(timeout_ms=30000, interval_ms=1000)
