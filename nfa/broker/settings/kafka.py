from typing import Literal, Optional

from pydantic import BaseModel, SecretStr, validator

from nfa.broker.enums import BrokerType

from .base import BaseBrokerSettings


class KafkaBrokerInstance(BaseModel):
    """Settings for a single Kafka broker instance"""
    host: str
    port: int = 9092  # Default Kafka port

    @property
    def address(self) -> str:
        """Get the address string for this broker instance"""
        return f"{self.host}:{self.port}"


class KafkaBrokerSettings(BaseBrokerSettings):
    """Settings specific to Kafka broker"""
    broker_type: Literal[BrokerType.faststream_kafka] = BrokerType.faststream_kafka
    instances: list[KafkaBrokerInstance]
    
    # Client settings
    client_id: str | None = None
    group_id: str | None = None
    
    # Security settings
    security_protocol: Literal["PLAINTEXT", "SSL", "SASL_PLAINTEXT", "SASL_SSL"] = "PLAINTEXT"
    sasl_mechanism: str | None = None
    sasl_username: str | None = None
    sasl_password: SecretStr | None = None
    sasl_kerberos_service_name: str = "kafka"
    sasl_kerberos_domain_name: str | None = None
    
    # Connection settings
    request_timeout_ms: int = 40000  # 40 seconds
    retry_backoff_ms: int = 100
    metadata_max_age_ms: int = 300000  # 5 minutes
    connections_max_idle_ms: int = 540000  # 9 minutes
    
    # Producer settings
    acks: Literal["0", "1", "all"] = "1"
    compression_type: Literal["gzip", "snappy", "lz4", "zstd"] | None = None
    max_batch_size: int = 16384  # 16KB
    max_request_size: int = 1048576  # 1MB
    linger_ms: int = 0
    enable_idempotence: bool = False
    transactional_id: str | None = None
    transaction_timeout_ms: int = 60000  # 1 minute
    
    # Consumer settings
    auto_offset_reset: Literal["earliest", "latest"] = "latest"
    enable_auto_commit: bool = True
    auto_commit_interval_ms: int = 5000
    max_poll_interval_ms: int = 300000
    max_poll_records: int = 500
    fetch_max_wait_ms: int = 500
    fetch_min_bytes: int = 1
    fetch_max_bytes: int = 52428800  # 50MB

    @validator("instances")
    def validate_instances(cls, v):
        if not v:
            raise ValueError("At least one Kafka broker instance must be specified")
        return v

    @property
    def bootstrap_servers(self) -> list[str]:
        """Get the list of Kafka broker addresses for the bootstrap servers"""
        return [instance.address for instance in self.instances]
