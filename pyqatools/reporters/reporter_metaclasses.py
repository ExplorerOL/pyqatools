import inspect
from abc import ABCMeta
from typing import _ProtocolMeta

from pyqatools.config.config_pyqatools import config_pyqatools
from pyqatools.loggers.logger_protocol import LoggerProtocol


class MetaclassWithMethodLoggingAndReporting(type):
    logger: LoggerProtocol

    def __new__(cls, name, bases, attrs):
        for attr_name, attr_value in attrs.items():
            # config_pyqatools.logger.deep_trace(f'Атрибут {attr_name} имеет тип {type(attr_value)}')
            if callable(attr_value) and not inspect.isclass(attr_value) and not attr_name.startswith('__'):
                if isinstance(attr_value, staticmethod):
                    # config_pyqatools.logger.deep_trace('Декорирование статического метода')
                    if config_pyqatools.reporter is not None and config_pyqatools.reporter.report_methods:
                        attrs[attr_name] = config_pyqatools.reporter.report_static_method(attrs[attr_name])
                    attrs[attr_name] = config_pyqatools.logger.log_static_method(attrs[attr_name])
                else:
                    # config_pyqatools.logger.deep_trace('Декорирование метода объекта')
                    if config_pyqatools.reporter is not None and config_pyqatools.reporter.report_methods:
                        attrs[attr_name] = config_pyqatools.reporter.report_method(attrs[attr_name])
                    attrs[attr_name] = config_pyqatools.logger.log_method(attrs[attr_name])
        attrs['logger'] = config_pyqatools.logger
        return super().__new__(cls, name, bases, attrs)


class MetaclassWithStepLoggingAndReporting(type):
    """Метакласс для репортинга шагов."""

    logger: LoggerProtocol

    def __new__(cls, name, bases, attrs):
        if config_pyqatools.reporter is not None:
            for attr_name, attr_value in attrs.items():
                if callable(attr_value) and not attr_name.startswith('_') and not (inspect.isclass(attr_value)):
                    if isinstance(attr_value, staticmethod):
                        if config_pyqatools.reporter is not None:
                            attrs[attr_name] = config_pyqatools.reporter.report_static_step(attrs[attr_name])
                        attrs[attr_name] = config_pyqatools.logger.log_static_step(attrs[attr_name])
                    else:
                        if config_pyqatools.reporter is not None:
                            attrs[attr_name] = config_pyqatools.reporter.report_step(attrs[attr_name])
                        attrs[attr_name] = config_pyqatools.logger.log_step(attrs[attr_name])
        attrs['logger'] = config_pyqatools.logger
        return super().__new__(cls, name, bases, attrs)


class MetaclassABCMetaWithMethodLoggingAndReporting(ABCMeta, MetaclassWithMethodLoggingAndReporting):
    pass


class MetaclassProtocolMetaWithMethodLoggingAndReporting(_ProtocolMeta, MetaclassWithMethodLoggingAndReporting):
    pass
