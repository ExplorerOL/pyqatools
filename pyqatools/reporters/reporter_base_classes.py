from abc import ABC
from typing import Protocol

from pyqatools.loggers.logger_protocol import LoggerProtocol
from pyqatools.reporters.reporter_metaclasses import (
    MetaclassProtocolMetaWithMethodLoggingAndReporting,
    MetaclassWithMethodLoggingAndReporting,
    MetaclassWithStepLoggingAndReporting,
)


class ClassWithStepLoggingAndReporting(metaclass=MetaclassWithStepLoggingAndReporting):
    logger: LoggerProtocol


class ClassWithMethodLoggingAndReporting(metaclass=MetaclassWithMethodLoggingAndReporting):
    logger: LoggerProtocol


class ABCWithMethodLoggingAndReporting(ABC, metaclass=MetaclassProtocolMetaWithMethodLoggingAndReporting):
    logger: LoggerProtocol


class ProtocolWithInstanceMethodLogging(Protocol, metaclass=MetaclassProtocolMetaWithMethodLoggingAndReporting):
    logger: LoggerProtocol
