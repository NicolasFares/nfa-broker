import logging
from typing import cast

from faststream.kafka import KafkaBroker as FaststreamKafkaBroker

from nfa.broker import Subscriber, Message
from nfa.broker.settings import KafkaBrokerSettings

from .faststream_broker import FaststreamBroker

logger = logging.getLogger(__name__)


class KafkaBroker(FaststreamBroker[KafkaBrokerSettings]):
    """Kafka broker implementation using FastStream"""

    def _create_broker(self) -> FaststreamKafkaBroker:
        """Create and configure the FastStream Kafka broker"""
        settings = cast(KafkaBrokerSettings, self._settings)

        return FaststreamKafkaBroker(
            # Connection settings
            bootstrap_servers=settings.bootstrap_servers,
            request_timeout_ms=settings.request_timeout_ms,
            retry_backoff_ms=settings.retry_backoff_ms,
            metadata_max_age_ms=settings.metadata_max_age_ms,
            connections_max_idle_ms=settings.connections_max_idle_ms,
            
            # Client settings
            client_id=settings.client_id,
            #
            # # Security settings
            # sasl_kerberos_service_name=settings.sasl_kerberos_service_name,
            # sasl_kerberos_domain_name=settings.sasl_kerberos_domain_name,
            #
            # # Producer settings
            # acks=settings.acks,
            # compression_type=settings.compression_type,
            # max_batch_size=settings.max_batch_size,
            # max_request_size=settings.max_request_size,
            # linger_ms=settings.linger_ms,
            # enable_idempotence=settings.enable_idempotence,
            # transactional_id=settings.transactional_id,
            # transaction_timeout_ms=settings.transaction_timeout_ms,
            #
            # Logging
            logger=logger,
            log_level=settings.log_level_int,
        )

    async def subscribe(
        self,
        subscriber: Subscriber,
        message_type: type[Message],
        timeout_sec: float | None = None,
    ) -> None:
        """Subscribe to messages of a specific type"""
        if not self._broker:
            raise RuntimeError("Broker is not initialized")
            
        routing_key = self.get_routing_key(message_type)
        logger.info(f"Subscribing {subscriber.__name__} to {routing_key}")
        
        try:
            consumer_config = {
                "auto_offset_reset": self._settings.auto_offset_reset,
                "auto_commit": self._settings.enable_auto_commit,
                "auto_commit_interval_ms": self._settings.auto_commit_interval_ms,
                "max_poll_interval_ms": self._settings.max_poll_interval_ms,
                "max_poll_records": self._settings.max_poll_records,
                "fetch_max_wait_ms": self._settings.fetch_max_wait_ms,
                "fetch_min_bytes": self._settings.fetch_min_bytes,
                "fetch_max_bytes": self._settings.fetch_max_bytes,
            }
            
            _subscribe = self._broker.subscriber(
                routing_key,
                **consumer_config,
                session_timeout_ms=int(timeout_sec * 1000) if timeout_sec else self._settings.timeout_ms,
            )
            _subscribe(subscriber)
            logger.debug(f"Successfully subscribed {subscriber.__name__} to {routing_key}")
        except Exception as e:
            logger.error(f"Failed to subscribe {subscriber.__name__} to {routing_key}: {e}")
            raise e

    async def publish(self, message: Message) -> None:
        """Publish a message to the broker"""
        if not self._broker:
            raise RuntimeError("Broker is not initialized")

        routing_key = self.get_routing_key(message)

        try:
            logger.info(f"Publishing {message} to {routing_key}")
            await self._broker.publish(message=message, topic=routing_key)

        except Exception as e:
            logger.error(f"Failed to publish {type(message).__name__} to {routing_key}: {e}")
            raise