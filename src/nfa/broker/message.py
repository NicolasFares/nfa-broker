from abc import ABC, abstractmethod

from pydantic import BaseModel


class BaseMessage(BaseModel, ABC):
    """
    Base message for commands and events.
    """

    id_user: str | None = None

    @staticmethod
    @abstractmethod
    def routing_key() -> str:
        """
        The routing key for the message.

        """
        pass
