from nfa.broker import Broker
from nfa.broker.settings import BrokerSettings
from nfa.broker.enums import BrokerType


def broker_factory(settings: BrokerSettings) -> Broker:
    match settings.broker_type:

        case BrokerType.faststream_kafka:
            try:
                from nfa.broker.adapters.faststream.kafka_broker import KafkaBroker
                return KafkaBroker(settings)
            
            except ImportError:
                raise ImportError("Please install the nfa-broker['kafka'] package to use the Kafka broker adapter")
            
        case BrokerType.faststream_rabbit:
            try:
                from nfa.broker.adapters.faststream.rabbit_broker import RabbitBroker
                return RabbitBroker(settings)
            
            except ImportError:
                raise ImportError("Please install the nfa-broker['rabbit'] package to use the RabbitMQ broker adapter")

        case _:
            raise NotImplementedError(f"Broker {settings.broker_type} not implemented")
