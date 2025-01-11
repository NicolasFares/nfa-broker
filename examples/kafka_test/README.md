# Kafka Broker Test

This example demonstrates how to use the Kafka broker implementation with a simple producer and consumer.

## Setup

1. Install the package with Kafka dependencies:
   ```bash
   pip install -e ".[kafka]"  # If installing from source
   # OR
   pip install "nfa-broker[kafka]"  # If installing from PyPI
   ```

2. Start the Kafka cluster:
   ```bash
   docker-compose up -d
   ```

3. Run the test script:
   ```bash
   python test_kafka.py
   ```

## What the Test Does

1. Checks if Kafka dependencies are available
2. Creates a Kafka broker with local settings
3. Subscribes to `TestMessage` events
4. Starts a consumer in the background
5. Runs a producer that sends 5 test messages
6. Waits for messages to be consumed
7. Cleans up and exits

## Expected Output

You should see logs showing:
1. Connection to Kafka
2. Subscription to messages
3. Consumer start
4. Messages being sent by the producer
5. Messages being received by the consumer
6. Clean shutdown

## Cleanup

To stop the Kafka cluster:
```bash
docker-compose down
```

## Note on Dependencies

This example requires the Kafka dependencies to be installed. The package supports both Kafka and RabbitMQ, but they are optional dependencies to keep the package lightweight. You can install:

- Just Kafka: `pip install "nfa-broker[kafka]"`
- Just RabbitMQ: `pip install "nfa-broker[rabbit]"`
- Both: `pip install "nfa-broker[kafka,rabbit]"`
