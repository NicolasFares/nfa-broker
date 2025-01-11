import asyncio
import logging
from collections import defaultdict
from typing import cast

from faststream.rabbit import RabbitBroker as FaststreamRabbitBroker, RabbitQueue, RabbitExchange
from pydantic import BaseModel

from nfa.broker import Subscriber
from nfa.broker.settings import RabbitBrokerSettings

from .faststream_broker import FaststreamBroker

logger = logging.getLogger(__name__)


class RabbitBroker(FaststreamBroker[RabbitBrokerSettings]):
    """RabbitMQ broker implementation using FastStream"""

    def __init__(self, settings: RabbitBrokerSettings):
        """Initialize the RabbitMQ broker with settings"""
        super().__init__(settings)
        self._settings = settings
        self._exchange: RabbitExchange | None = None
        self._message_type_to_queues: dict[type[BaseModel], set[RabbitQueue]] = defaultdict(set)

    def _create_broker(self) -> FaststreamRabbitBroker:
        """Create and configure the FastStream RabbitMQ broker"""
        settings = cast(RabbitBrokerSettings, self._settings)
        
        # Create the exchange if it doesn't exist
        self._exchange = RabbitExchange(
            settings.exchange,
            durable=settings.queue_durable,
            auto_delete=settings.queue_auto_delete,
        )
        
        return FaststreamRabbitBroker(
            host=settings.host,
            port=settings.port,
            login=settings.user,
            password=settings.password.get_secret_value() if settings.password else None,
            virtualhost=settings.virtual_host,
            ssl=settings.ssl,
            logger=logger,
            log_level=settings.log_level_int,
            heartbeat=settings.heartbeat,
        )

    async def subscribe(
        self,
        subscriber: Subscriber,
        message_type: type[BaseModel],
        timeout_sec: float | None = None,
    ) -> None:
        """Subscribe to messages of a specific type"""
        if not self._broker or not self._exchange:
            raise RuntimeError("Broker is not initialized")
            
        queue_routing_key = self.get_routing_key(subscriber, message_type)
        logger.info(f"Subscribing {subscriber.__name__} to {queue_routing_key}")

        try:
            # Create queue with settings
            queue = RabbitQueue(
                name=queue_routing_key,
                routing_key=queue_routing_key,
                durable=self._settings.queue_durable,
                auto_delete=self._settings.queue_auto_delete,
                exclusive=False,
                max_priority=self._settings.queue_max_priority,
            )

            # Prepare and apply the subscription
            _subscribe = self._broker.subscriber(
                queue,
                self._exchange,
                timeout=(timeout_sec * 1000) or self._settings.consumer_timeout,
                prefetch_count=self._settings.prefetch_count,
            )
            _subscribe(subscriber)

            # Track the queue for publishing
            self._message_type_to_queues[message_type].add(queue)
            logger.debug(f"Successfully subscribed {subscriber.__name__} to {queue_routing_key}")
            
        except Exception as e:
            logger.error(f"Failed to subscribe {subscriber.__name__} to {queue_routing_key}: {e}")
            raise

    async def publish(self, message: BaseModel) -> None:
        """Publish a message to all queues of its type"""
        if not self._broker or not self._exchange:
            raise RuntimeError("Broker is not initialized")

        queues = self._message_type_to_queues[type(message)]
        if not queues:
            logger.warning(f"No queues found for message type {type(message)}")
            return

        logger.info(f"Publishing {type(message).__name__} to {len(queues)} queues")
        
        try:
            # Publish to all queues in parallel
            await asyncio.gather(
                *[
                    self._broker.publish(
                        message=message,
                        queue=queue,
                        exchange=self._exchange,
                        mandatory=self._settings.mandatory,
                        delivery_mode=self._settings.delivery_mode,
                    )
                    for queue in queues
                ]
            )
            logger.debug(f"Successfully published {type(message).__name__} to all queues")
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            raise
