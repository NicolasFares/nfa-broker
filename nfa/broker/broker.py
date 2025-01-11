import abc
from typing import Any, Awaitable, Callable, TypeVar, Generic

from pydantic import BaseModel

from nfa.broker.settings import BaseBrokerSettings

Subscriber = Callable[[Any], Awaitable[Any]]
T = TypeVar('T', bound=BaseBrokerSettings)
Message = TypeVar('Message', bound=BaseModel)


class Broker(abc.ABC, Generic[T]):
    """
    Abstract base class for message brokers.
    
    Generic type T specifies the settings type this broker accepts.
    """

    def __init__(self, settings: T):
        """
        Initialize the broker with type-safe settings.

        Args:
            settings: Broker-specific settings instance
        """
        self._settings = settings
        self._is_running: bool = False
        self._broker = None

    @property
    def is_running(self) -> bool:
        """Check if the broker is currently running"""
        return self._is_running

    @abc.abstractmethod
    async def open(self) -> None:
        """
        Open the broker connection.
        
        Should be called before any other operations.
        Raises:
            ConnectionError: If connection cannot be established
        """
        pass

    @abc.abstractmethod
    async def close(self) -> None:
        """
        Close the broker connection and cleanup resources.
        """
        pass

    @abc.abstractmethod
    async def subscribe(
        self,
        subscriber: Subscriber,
        message_type: type[Message],
        timeout_sec: float | None = None,
    ) -> None:
        """
        Subscribe a handler to messages of a specific type.

        Args:
            subscriber: The handler to subscribe
            message_type: The type of messages to subscribe to
            timeout_sec: Optional timeout for the handler in seconds
        """
        pass


    @abc.abstractmethod
    async def publish(self, message: Message) -> None:
        """
        Publish a message via the broker.

        Args:
            message: The message to publish

        Raises:
            RuntimeError: If broker is not running
        """
        pass

    async def start(self) -> None:
        """
        Start consuming messages from the broker.
        
        This method should handle message routing to appropriate subscribers.
        
        Raises:
            RuntimeError: If broker is not running
        """

        if not self.is_running:
            await self.open()

        await self._start()

    @abc.abstractmethod
    async def _start(self) -> None:
        """
        Start consuming messages from the broker.

        This method should handle message routing to appropriate subscribers.

        Raises:
            RuntimeError: If broker is not running
        """
        pass

    @staticmethod
    def get_routing_key(message: type[Message] | Message, message_queue_suffix: str | None = None) -> str:
        """
        Build the routing key for a subscriber and a message type.

        Args:
            message: The message type or instance
            message_queue_suffix: Optional subscriber queue name suffix

        Returns:
            str: The routing key

        Note:
            If 'message' has a routing_key attribute, it will be used directly.
            If 'message' has a routing_key method, it will be called.
            If 'message' is a BaseModel, its __name__ will be used.
        """
        routing_key = getattr(message, "routing_key", None)
        if callable(routing_key):
            built_routing_key = routing_key()
            if not isinstance(built_routing_key, str):
                raise ValueError(f"Fetched routing key from message must be a string. Got: {built_routing_key}")

            return built_routing_key

        elif isinstance(routing_key, str):
            return routing_key

        message_queue = message.__name__

        if message_queue_suffix is not None:
            return f"{message_queue_suffix}.{message_queue}"

        return message_queue
