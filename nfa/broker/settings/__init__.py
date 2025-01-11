"""
Broker settings module.

This module provides settings classes for different message broker implementations.
"""
from typing import Union

from nfa.broker.settings.base import BaseBrokerSettings
from nfa.broker.settings.kafka import KafkaBrokerInstance, KafkaBrokerSettings
from nfa.broker.settings.rabbitmq import RabbitBrokerSettings

# Type alias for all possible broker settings
BrokerSettings = Union[KafkaBrokerSettings, RabbitBrokerSettings]

__all__ = [
    'BaseBrokerSettings',
    'BrokerSettings',
    'KafkaBrokerInstance',
    'KafkaBrokerSettings',
    'RabbitBrokerSettings',
]
