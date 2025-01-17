import asyncio
import json

from redis.asyncio import Redis

from core.config import settings
from schemas.kafka import KafkaMessage
from services.kafka_producer import get_kafka_producer_service


async def process_redis_queue(redis: Redis) -> None:
    """
    Фоновая задача для обработки очереди событий в Redis и отправки их в Kafka пачками.
    """
    kafka_producer_service = await get_kafka_producer_service()
    await kafka_producer_service.start()
    try:
        while True:
            events = await redis.lrange(
                settings.kafka_topic_name, 0, settings.kafka_batch_size - 1
            )
            if events:
                await redis.ltrim(
                    settings.kafka_topic_name, settings.kafka_batch_size, -1
                )
                events = [json.loads(event) for event in events]
                await kafka_producer_service.send_batch_messages(
                    [KafkaMessage(key=event.get("event_type"), value=event) for event in events]
                )
            await asyncio.sleep(settings.kafka_batch_sleep)
    finally:
        await kafka_producer_service.stop()
