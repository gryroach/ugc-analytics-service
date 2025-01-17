import random
from contextlib import asynccontextmanager

from aiokafka.producer import AIOKafkaProducer

from core.config import settings
from schemas.kafka import KafkaMessage


class KafkaProducerService:
    def __init__(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_server,
            retry_backoff_ms=settings.kafka_retry_backoff_ms,
        )

    @asynccontextmanager
    async def kafka_producer(self) -> AIOKafkaProducer:
        await self.start()
        try:
            yield self.producer
        finally:
            await self.stop()

    async def start(self):
        await self.producer.start()

    async def stop(self):
        await self.producer.stop()

    async def send_message(self, message: str | bytes, key: str | None) -> None:
        if isinstance(message, str):
            message = message.encode("utf-8")
        if isinstance(key, str):
            key = key.encode("utf-8")
        async with self.kafka_producer() as producer:
            await producer.send_and_wait(
                topic=settings.kafka_topic_name,
                value=message,
                key=key,
            )

    async def send_batch_messages(self, messages: list[KafkaMessage]) -> None:
        batch = self.producer.create_batch()
        for message in messages:
            batch.append(
                key=message.key,
                value=message.value,
                timestamp=None,
            )
        partitions = await self.producer.partitions_for(topic=settings.kafka_topic_name)
        partition = random.choice(tuple(partitions))
        await self.producer.send_batch(
            batch=batch,
            topic=settings.kafka_topic_name,
            partition=partition,
        )


async def get_kafka_producer_service() -> KafkaProducerService:
    return KafkaProducerService()
