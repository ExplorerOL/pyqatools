import inspect
from abc import ABCMeta
from typing import _ProtocolMeta

from pyqatools.config.config_pyqatools import config_pyqatools
from pyqatools.loggers.logger_protocol import LoggerProtocol


class MetaclassWithMethodLogging(type):
    """Метакласс для логгирования методов.

    Декоратор логгирования метода применяется ко всем атрибутам класса, которые имеют тип
    Callable и не являются классом. Для статического метода и метода объекта применяются разные
    декораторы.
    """

    logger: LoggerProtocol

    def __new__(cls, name, bases, attrs):
        for attr_name, attr_value in attrs.items():
            if callable(attr_value) and not inspect.isclass(attr_value):
                if isinstance(attr_value, staticmethod):
                    attrs[attr_name] = config_pyqatools.logger.log_static_method(attr_value)
                else:
                    attrs[attr_name] = config_pyqatools.logger.log_method(attr_value)
        attrs['logger'] = config_pyqatools.logger
        return super().__new__(cls, name, bases, attrs)


class MetaclassWithStepLogging(type):
    """Метакласс для логгирования шагов.

    Декоратор логгирования шага применяется ко всем атрибутам класса, которые имеют тип
    Callable, не являются классом и не начинаются с _
    """

    logger: LoggerProtocol

    def __new__(cls, name, bases, attrs):
        for attr_name, attr_value in attrs.items():
            if callable(attr_value) and not attr_name.startswith('_') and not (inspect.isclass(attr_value)):
                if isinstance(attr_value, staticmethod):
                    attrs[attr_name] = config_pyqatools.logger.log_static_step(attr_value)
                else:
                    attrs[attr_name] = config_pyqatools.logger.log_step(attr_value)

        attrs['logger'] = config_pyqatools.logger

        return super().__new__(cls, name, bases, attrs)


class MetaclassABCMetaWithMethodLogging(ABCMeta, MetaclassWithMethodLogging):
    pass


class MetaclassProtocolMetaWithMethodLogging(_ProtocolMeta, MetaclassWithMethodLogging):
    pass
