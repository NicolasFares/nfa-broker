from typing import Literal

from pydantic import SecretStr, validator

from nfa.broker.enums import BrokerType

from .base import BaseBrokerSettings


class RabbitBrokerSettings(BaseBrokerSettings):
    """Settings specific to RabbitMQ broker"""
    broker_type: Literal[BrokerType.faststream_rabbit] = BrokerType.faststream_rabbit
    host: str
    port: int
    user: str | None = None
    password: SecretStr | None = None
    virtual_host: str = "/"
    exchange: str = "public"
    heartbeat: int = 60
    ssl: bool = False
    
    # Queue settings
    queue_max_priority: int | None = None
    queue_durable: bool = True
    queue_auto_delete: bool = False
    
    # Consumer settings
    prefetch_count: int = 1
    consumer_timeout: float | None = None
    
    # Publisher settings
    delivery_mode: Literal[1, 2] = 2  # 1: non-persistent, 2: persistent
    mandatory: bool = False
    
    @validator("heartbeat")
    def validate_heartbeat(cls, v):
        if v < 0:
            raise ValueError("Heartbeat must be non-negative")
        return v
        
    @validator("prefetch_count")
    def validate_prefetch_count(cls, v):
        if v < 1:
            raise ValueError("Prefetch count must be positive")
        return v

    @property
    def socket_address(self) -> str:
        """Get the socket address string"""
        return f"{self.host}:{self.port}"
