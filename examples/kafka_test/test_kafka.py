import asyncio
import logging
import sys
from typing import Any

from nfa.broker import Broker
from nfa.broker.settings import KafkaBrokerSettings, KafkaBrokerInstance
from nfa.broker.adapters.faststream import get_kafka_broker, BrokerNotAvailable

# from faststream.kafka import KafkaBroker as FaststreamKafkaBroker

from models import TestMessage


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def message_handler(message: TestMessage) -> Any:
    """Handle incoming test messages"""
    logger.info(f"Received message: {message}")
    return message


async def run_producer(broker: Broker) -> None:
    """Run the producer to send test messages"""
    try:
        # Send 5 test messages
        for i in range(5):
            message = TestMessage(id=i, content=f"Test message {i}")
            logger.info(f"Sending message: {message}")
            # await broker.publish(message=message, topic=TestMessage.routing_key())
            await broker.publish(message=message)
            # Wait a bit between messages
            await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"Error in producer: {e}")
        raise


async def main():
    try:
        # Get the Kafka broker implementation
        KafkaBroker = get_kafka_broker()
        pass
    except BrokerNotAvailable as e:
        logger.error(str(e))
        sys.exit(1)

    # Create broker settings
    settings = KafkaBrokerSettings(
        instances=[
            KafkaBrokerInstance(host="localhost", port=9092)
        ],
        group_id="test-group",
        client_id="test-client",
    )

    # Create and configure the broker
    # broker = FaststreamKafkaBroker(bootstrap_servers="localhost:9092")
    test_broker = KafkaBroker(settings)

    try:
        # Connect to Kafka
        # await broker.connect()
        await test_broker.open()
        logger.info("Connected to Kafka")

        # Subscribe to messages
        # subscribe = broker.subscriber(TestMessage.routing_key())
        # subscribe(message_handler)

        await test_broker.subscribe(message_handler, TestMessage)
        logger.info("Subscribed to TestMessage")

        # Start the consumer in the background
        # await broker.start()
        await test_broker.start()
        logger.info("Started consumer")

        # Run the producer
        await run_producer(test_broker)
        logger.info("Producer finished")

        # Wait a bit to ensure all messages are consumed
        await asyncio.sleep(2)

    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise
    finally:
        # Clean up
        await test_broker.close()
        logger.info("Closed broker connection")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
