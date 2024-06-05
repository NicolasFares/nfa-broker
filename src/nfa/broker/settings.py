import logging

from pydantic import SecretStr
from pydantic_settings import BaseSettings

from nfa.broker.enums import BrokerType


class BrokerSettings(BaseSettings):
    host: str
    port: int
    user: str | None = None
    password: SecretStr | None = None
    virtual_host: str | None = None
    exchange: str = "public"
    heartbeat: int = 60
    ssl: bool = False
    log_level: str = "INFO"
    broker_type: BrokerType = BrokerType.faststream_kafka

    @property
    def socket_address(self) -> str:
        return f"{self.host}:{self.port}"

    @property
    def log_level_int(self) -> int:
        level = self.log_level.upper()
        if not hasattr(logging, level):
            raise ValueError(f"Invalid log level {self.log_level}")

        return getattr(logging, level)
