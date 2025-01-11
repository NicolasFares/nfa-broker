from enum import StrEnum


class BrokerType(StrEnum):
    """
    Enum for different broker types
    """
    faststream_kafka = "faststream.kafka"
    faststream_rabbit = "faststream.rabbit"