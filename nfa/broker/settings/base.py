import logging
from typing import Union

from pydantic import BaseModel, validator


class BaseBrokerSettings(BaseModel):
    """Base settings shared by all brokers"""
    log_level: str = "INFO"
    timeout_ms: int = 1000 * 10

    @property
    def log_level_int(self) -> int:
        level = self.log_level.upper()
        if not hasattr(logging, level):
            raise ValueError(f"Invalid log level {self.log_level}")
        
        return getattr(logging, level)

    @validator("timeout_ms")
    def validate_timeout(cls, v):
        if v <= 0:
            raise ValueError("Timeout must be positive")
        return v


