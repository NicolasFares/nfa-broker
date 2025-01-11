"""FastStream broker adapters.

This module provides FastStream-based broker implementations.
The actual broker implementations (Kafka, RabbitMQ) are loaded lazily
based on which optional dependencies are installed.
"""
from importlib import util
from typing import Type

from nfa.broker import Broker


class BrokerNotAvailable(ImportError):
    """Raised when trying to use a broker whose dependencies are not installed."""
    
    def __init__(self, broker_type: str):
        super().__init__(
            f"{broker_type} broker is not available. "
            f"Please install the required dependencies with: "
            f"pip install 'nfa-broker[{broker_type.lower()}]'"
        )


def is_kafka_available() -> bool:
    """Check if Kafka dependencies are available"""
    return util.find_spec("faststream.kafka") is not None


def is_rabbit_available() -> bool:
    """Check if RabbitMQ dependencies are available"""
    return util.find_spec("faststream.rabbit") is not None


def get_kafka_broker() -> Type[Broker]:
    """Get the Kafka broker implementation.
    
    Returns:
        Type[Broker]: The Kafka broker class.
        
    Raises:
        BrokerNotAvailable: If Kafka dependencies are not installed.
    """
    if not is_kafka_available():
        raise BrokerNotAvailable("Kafka")
    from .kafka_broker import KafkaBroker
    return KafkaBroker


def get_rabbit_broker() -> Type[Broker]:
    """Get the RabbitMQ broker implementation.
    
    Returns:
        Type[Broker]: The RabbitMQ broker class.
        
    Raises:
        BrokerNotAvailable: If RabbitMQ dependencies are not installed.
    """
    if not is_rabbit_available():
        raise BrokerNotAvailable("RabbitMQ")
    from .rabbit_broker import RabbitBroker
    return RabbitBroker


__all__ = [
    "BrokerNotAvailable",
    "is_kafka_available",
    "is_rabbit_available",
    "get_kafka_broker",
    "get_rabbit_broker",
]