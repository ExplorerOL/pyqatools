from typing import Callable, Iterable

import testit
from testit_python_commons.decorators import inner
from testit_python_commons.services.logger import adapter_logger

from pyqatools.integrations.tms.integration_tms_protocol import IntegrationTMSProtocol


class IntegrationTestIT(IntegrationTMSProtocol):
    """Класс для интеграции с TestIT."""

    @staticmethod
    @adapter_logger
    def __generate_external_id():
        """Декоратор для генерации externalId для TestIT."""

        def outer(function):
            function.test_external_id = function.__name__
            return inner(function)

        return outer

    @staticmethod
    def __work_items_ids(id: int):
        """Декоратор для привязки к ручному тест-кейса с указанным id в TestIT.

        Параметры:
            id (int): id ручного тест-кейса в ТестИТ
        """
        return testit.workItemIds(id)

    @staticmethod
    @adapter_logger
    def __generate_display_name():
        """Декоратор для генерации displayName для TestIT."""

        def outer(function):
            function.test_displayname = function.__doc__
            return inner(function)

        return outer

    @staticmethod
    def generate_autotest_data(manual_case_id: int) -> Callable:
        """Декоратор для генерации данных для TestIT.

        Параметры:
            testit_case_id (int): id ручного тест-кейса в ТестИТ
        """

        def outer(function):
            IntegrationTestIT.__work_items_ids(id=manual_case_id)(function)
            IntegrationTestIT.__generate_external_id()(function)
            IntegrationTestIT.__generate_display_name()(function)
            return inner(function)

        return outer

    @staticmethod
    def add_links(
        url: str,
        link_type: IntegrationTMSProtocol.LinkType,
        title: str | None = None,
        description: str | None = None,
        links: Iterable | None = None,
    ):
        """Добавление ссылок для результата кейса TestIT."""
        if not title:
            title = url
        if not description:
            description = link_type
        testit.addLinks(url=url, title=title, type=link_type, description=description, links=links)

    @staticmethod
    def get_manual_case_ids_from_request_fixture(request) -> list[int] | None:
        if hasattr(request.function, 'test_workitems_id'):
            return request.function.test_workitems_id
        else:
            return None
