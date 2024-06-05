import abc
from typing import Any, Awaitable, Callable, Type

from nfa.broker.message import BaseMessage
from nfa.broker.settings import BrokerSettings

Subscriber = Callable[[BaseMessage], Awaitable[Any]]


class Broker(abc.ABC):

    def __init__(self, settings: BrokerSettings):
        self.settings = settings

    @abc.abstractmethod
    async def open(self):
        """
        Open the broker.
        """
        pass

    @abc.abstractmethod
    async def close(self):
        """
        Close the broker.
        """
        pass

    @abc.abstractmethod
    async def subscribe(
        self,
        subscriber: Subscriber,
        message_type: type[BaseMessage],
        timeout: float | None = None,
    ) -> None:
        """
        Subscribe a handler to messages of a specific type.

        :param subscriber: The handler to subscribe.
        :param message_type: The type of messages to subscribe to.
        :param timeout: The timeout for the handler.
        """
        pass

    @abc.abstractmethod
    async def unsubscribe(self, subscriber_type: Type[Subscriber]) -> None:
        """
        Unsubscribe a handler from all messages it was subscribed to.

        :param subscriber_type: The type of the handler to unsubscribe.

        """
        pass

    @abc.abstractmethod
    async def publish(self, message: BaseMessage) -> None:
        """
        Publish a message via the broker.

        Args:
            message: The message to publish.
        """
        pass

    @abc.abstractmethod
    async def start(self):
        """
        Wait for messages from the broker and consume them when any.
        """
        pass

    @staticmethod
    def build_routing_key(subscriber: Subscriber, message_type: type[BaseMessage]) -> str:
        """
        Build the routing key for a subscriber and a message type.

        :param subscriber: The subscriber.
        :param message_type: The message type.
        :return: The routing key.
        """

        module = subscriber.__module__
        class_name = subscriber.__class__.__name__

        return f"{module}.{class_name}.{message_type.routing_key()}"
