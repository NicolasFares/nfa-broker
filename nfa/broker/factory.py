from nfa.broker import Broker
from nfa.broker.settings import BrokerSettings
from nfa.broker.enums import BrokerType
from nfa.broker.adapters.faststream import get_kafka_broker, get_rabbit_broker, BrokerNotAvailable


def broker_factory(settings: BrokerSettings) -> Broker:
    match settings.broker_type:

        case BrokerType.faststream_kafka:
            broker_class = get_kafka_broker()
            return broker_class(settings)

        case BrokerType.faststream_rabbit:
            broker_class = get_rabbit_broker()
            return broker_class(settings)

        case _:
            raise BrokerNotAvailable(settings.broker_type)
