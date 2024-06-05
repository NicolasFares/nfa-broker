import asyncio
import logging
from collections import defaultdict

from faststream.rabbit import RabbitBroker as FaststreamRabbitBroker, RabbitQueue, RabbitExchange

from nfa.broker.message import BaseMessage
from nfa.broker import Subscriber
from nfa.broker.settings import BrokerSettings

from .faststream_broker import FaststreamBroker

logger = logging.getLogger(__name__)


class RabbitBroker(FaststreamBroker):

    def __init__(self, settings: BrokerSettings):
        super().__init__(settings)

        self._broker: FaststreamRabbitBroker = self._create_broker(settings)
        self._exchange = RabbitExchange(settings.exchange, durable=True)
        self._message_type_to_queues: dict[type[BaseMessage], set[RabbitQueue]] = defaultdict(set)

    def _create_broker(self, settings: BrokerSettings) -> FaststreamRabbitBroker:
        return FaststreamRabbitBroker(
            logger=logger,
            log_level=settings.log_level_int,
            host=settings.host,
            port=settings.port,
            login=settings.user if settings.user else None,
            password=settings.password.get_secret_value() if settings.password else None,
            virtualhost=settings.virtual_host,
        )

    async def subscribe(
        self, subscriber: Subscriber, message_type: type[BaseMessage], timeout: float | None = None
    ) -> None:
        queue_routing_key = self.build_routing_key(subscriber, message_type)

        logger.info(f"Subscribing {type(subscriber)} to {queue_routing_key}")

        queue = RabbitQueue(
            name=queue_routing_key,
            routing_key=queue_routing_key,
            durable=True,
            auto_delete=False,
            exclusive=False,
        )

        # Prepare the subscriber
        _subscribe = self._broker.subscriber(queue, self._exchange)

        # Subscribe the subscriber
        _subscribe(subscriber)

        # Add the queue to the message type
        self._message_type_to_queues[message_type].add(queue)

    async def publish(self, message: BaseMessage) -> None:
        queues = self._message_type_to_queues[type(message)]

        logger.info(f"Publishing {message} to {[queue.name for queue in queues]}")

        await asyncio.gather(
            *[
                self._broker.publish(
                    message=message,
                    queue=queue,
                    exchange=self._exchange,
                )
                for queue in queues
            ]
        )
