from abc import ABC, abstractmethod
import logging
from typing import Generic, TypeVar

from faststream.broker.core.usecase import BrokerUsecase

from nfa.broker import Broker
from nfa.broker.settings import BaseBrokerSettings


logger = logging.getLogger(__name__)

SettingsType = TypeVar("SettingsType", bound=BaseBrokerSettings)


class FaststreamBroker(Broker[SettingsType], ABC, Generic[SettingsType]):
    """
    Base class for FastStream-based brokers.
    
    This class handles common FastStream broker operations and state management.
    """
    @abstractmethod
    def _create_broker(self) -> BrokerUsecase:
        """Create and configure the FastStream broker instance"""
        pass

    async def open(self) -> None:
        """Open the broker connection"""
        if self._is_running:
            logger.warning("Broker is already running")
            return

        if self._broker is None:
            self._broker = self._create_broker()
        
        try:
            await self._broker.connect()
            self._is_running = True
            logger.info("Successfully connected to broker")
        except Exception as e:
            self._is_running = False
            logger.error(f"Failed to connect to broker: {e}")
            raise ConnectionError(f"Failed to connect to broker: {e}") from e

    async def close(self) -> None:
        """Close the broker connection"""
        if not self._is_running:
            logger.warning("Broker is not running")
            return

        if self._broker is not None:
            try:
                await self._broker.close()
                logger.info("Successfully closed broker connection")
            except Exception as e:
                logger.error(f"Error closing broker connection: {e}")
                raise
            finally:
                self._is_running = False
                self._broker = None

    async def _start(self) -> None:
        """Start consuming messages"""
        if not self._broker:
            raise RuntimeError("Broker is not initialized")
            
        try:
            logger.info("Starting message consumption")
            await self._broker.start()
        except Exception as e:
            logger.error(f"Error during message consumption: {e}")
            raise
