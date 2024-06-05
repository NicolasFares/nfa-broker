from abc import ABC, abstractmethod
from typing import Type

from faststream.broker.core.asynchronous import BrokerAsyncUsecase

from dalt.broker import Broker, Subscriber
from dalt.broker.settings import BrokerSettings
from dalt.sdk.domain import BaseMessage
from dalt.sdk.logging import get_logger

logger = get_logger(__name__)


class FaststreamBroker(Broker, ABC):
    _broker: BrokerAsyncUsecase

    @abstractmethod
    def _create_broker(self, settings: BrokerSettings) -> BrokerAsyncUsecase:
        pass

    async def open(self):
        await self._broker.connect()

    async def close(self):
        await self._broker.close()

    async def unsubscribe(self, subscriber_type: Type[Subscriber]) -> None:
        raise NotImplementedError

    async def publish(self, message: BaseMessage) -> None:
        await self._broker.publish(message, message.get_routing_key())

    async def start(self):
        logger.info("Starting broker...")

        await self._broker.start()
