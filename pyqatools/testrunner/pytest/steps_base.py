import inspect

from pyqatools.config.config_pyqatools import config_pyqatools
from pyqatools.loggers.logger_protocol import LoggerProtocol
from pyqatools.retryers.retryer_config import RetryConfigs


class StepsBaseMetaclass(type):
    """Метакласс для шагов."""

    logger: LoggerProtocol

    def __new__(cls, name, bases, attrs):
        for attr_name, attr_value in attrs.items():
            if callable(attr_value) and not attr_name.startswith('_') and not (inspect.isclass(attr_value)):
                if attr_name.startswith('wait_auto_for_') and config_pyqatools.retryer is not None:
                    attrs[attr_name] = config_pyqatools.retryer.retry(RetryConfigs.T30000_I1000.value)(attrs[attr_name])
                if isinstance(attr_value, staticmethod):
                    if config_pyqatools.reporter is not None:
                        attrs[attr_name] = config_pyqatools.reporter.report_static_step(attrs[attr_name])
                    attrs[attr_name] = config_pyqatools.logger.log_static_step(attrs[attr_name])
                else:
                    if config_pyqatools.reporter is not None:
                        attrs[attr_name] = config_pyqatools.reporter.report_step(attrs[attr_name])
                    attrs[attr_name] = config_pyqatools.logger.log_step(attrs[attr_name])
                if attr_name.startswith('verify_soft_') and config_pyqatools.assert_soft is not None:
                    attrs[attr_name] = config_pyqatools.assert_soft.assert_soft_for_method(attrs[attr_name])

                if attr_name.endswith('_with_auto_retry') and config_pyqatools.retryer is not None:
                    attrs[attr_name] = config_pyqatools.retryer.retry(RetryConfigs.T30000_I1000.value)(attrs[attr_name])

        attrs['logger'] = config_pyqatools.logger
        return super().__new__(cls, name, bases, attrs)


class StepsBase(metaclass=StepsBaseMetaclass):
    pass
