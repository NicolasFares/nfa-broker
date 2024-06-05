from dalt.sdk import logging

from faststream.kafka import KafkaBroker as FaststreamKafkaBroker

from dalt.sdk.domain import BaseMessage
from dalt.broker import Subscriber
from dalt.broker.settings import BrokerSettings

from .faststream_broker import FaststreamBroker

logger = logging.get_logger(__name__)


class KafkaBroker(FaststreamBroker):

    def __init__(self, settings: BrokerSettings):
        super().__init__(settings)

        self._broker: FaststreamKafkaBroker = self._create_broker(settings)

    def _create_broker(self, settings: BrokerSettings) -> FaststreamKafkaBroker:
        return FaststreamKafkaBroker(
            bootstrap_servers=settings.socket_address,
            logger=logger,
            log_level=settings.log_level_int,
        )

    async def subscribe(
        self, subscriber: Subscriber, message_type: type[BaseMessage], timeout: float | None = None
    ) -> None:
        # Prepare the subscriber
        timeout_ms = int(timeout * 1000) if timeout else None
        _subscribe = self._broker.subscriber(message_type.get_routing_key(), session_timeout_ms=timeout_ms)

        # Subscribe the subscriber
        _subscribe(subscriber)
