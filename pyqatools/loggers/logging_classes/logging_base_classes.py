from abc import ABC
from typing import Protocol

from pyqatools.loggers.logger_protocol import LoggerProtocol
from pyqatools.loggers.logging_classes.logging_metaclasses import (
    MetaclassABCMetaWithMethodLogging,
    MetaclassProtocolMetaWithMethodLogging,
    MetaclassWithMethodLogging,
    MetaclassWithStepLogging,
)


class ABCWithMethodLogging(ABC, metaclass=MetaclassABCMetaWithMethodLogging):
    logger: LoggerProtocol


class ClassWithMethodLogging(metaclass=MetaclassWithMethodLogging):
    logger: LoggerProtocol


class ClassWithStepLogging(metaclass=MetaclassWithStepLogging):
    logger: LoggerProtocol


class ProtocolWithInstanceMethodLogging(Protocol, metaclass=MetaclassProtocolMetaWithMethodLogging):
    logger: LoggerProtocol
