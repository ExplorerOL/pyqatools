import enum
from typing import Callable, Iterable, Protocol

from testit_python_commons.models import LinkType as _LinkType


class IntegrationTMSProtocol(Protocol):
    """Протокол для интеграции с TMS."""

    class LinkType(enum.Enum):
        """Тип ссылки."""

        RELATED = _LinkType.RELATED
        BLOCKED_BY = _LinkType.BLOCKED_BY
        DEFECT = _LinkType.DEFECT
        ISSUE = _LinkType.ISSUE
        REQUIREMENT = _LinkType.REQUIREMENT
        REPOSITORY = _LinkType.REPOSITORY

    @staticmethod
    def generate_autotest_data(manual_case_id: int) -> Callable: ...

    @staticmethod
    def add_links(
        url: str,
        link_type: LinkType,
        title: str | None = None,
        description: str | None = None,
        links: Iterable | None = None,
    ) -> None:
        """Добавление ссылок для результата кейса TestIT."""
