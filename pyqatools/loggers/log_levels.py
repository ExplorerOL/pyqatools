import enum


class LogLevels(enum.Enum):
    """Перечень уровней логгирования."""

    DEEP_TRACE = 4
    TRACE = 5
    TEST = 9
    DEBUG = 10
    INFO = 20
    STEP = 21
    FIXTURE = 22
    SUCCESS = 25
    WARNING = 30
    ERROR = 40
