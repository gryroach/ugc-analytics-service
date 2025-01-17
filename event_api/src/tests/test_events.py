import json
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from fastapi import Request
from redis.asyncio import Redis

from core.config import settings
from schemas.events import SignUpEvent
from services.background_tasks import process_redis_queue
from services.events import process_event
from services.kafka_producer import KafkaProducerService


@pytest_asyncio.fixture
async def redis_client():
    redis = Redis(
        host=settings.test_redis_host,
        port=settings.test_redis_port,
        db=settings.test_redis_db,
    )
    await redis.flushdb()
    yield redis
    await redis.aclose()


@pytest_asyncio.fixture
def mock_request():
    request = AsyncMock(spec=Request)
    request.headers.get.return_value = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/58.0.3029.110 Safari/537.3"
    )
    request.client.host = "192.168.1.1"
    return request


@pytest_asyncio.fixture
async def mock_credentials():
    return {
        "auth_type": "verified",
        "user": "test_user",
        "role": "admin",
    }


@pytest.mark.asyncio
async def test_process_event(redis_client, mock_request, mock_credentials):
    event = SignUpEvent(
        email="test@example.com",
        registration_method="email",
        timestamp=datetime.now(),
        device_id="device_123",
        device_type="mobile",
        country="USA",
        region="CA",
        city="San Francisco",
        session_id="session_123",
        session_start_time=datetime.now(),
        session_end_time=datetime.now(),
        extra_info={"key": "value"},
    )

    processed_event = await process_event(
        event, mock_request, mock_credentials, redis_client
    )
    assert processed_event.ip_address == "192.168.1.1"
    assert processed_event.user_role == "admin"
    assert processed_event.browser == "Chrome"

    # Проверяем, что событие было записано в Redis
    events = await redis_client.lrange(settings.kafka_topic_name, 0, -1)
    assert len(events) == 1
    stored_event = json.loads(events[0])
    assert stored_event["email"] == event.email
    assert stored_event["registration_method"] == event.registration_method


@pytest.mark.asyncio
async def test_process_redis_queue(
    redis_client, mock_request, mock_credentials, mocker
):
    mocker.patch.object(
        KafkaProducerService, "send_batch_messages", AsyncMock(return_value=None)
    )

    event = SignUpEvent(
        email="test@example.com",
        registration_method="email",
        timestamp=datetime.now(),
        device_id="device_123",
        device_type="mobile",
        country="USA",
        region="CA",
        city="San Francisco",
        session_id="session_123",
        session_start_time=datetime.now(),
        session_end_time=datetime.now(),
        extra_info={"key": "value"},
    )

    # Записываем событие в Redis
    await process_event(event, mock_request, mock_credentials, redis_client)
    # Проверяем, что событие было записано в Redis
    events = await redis_client.lrange(settings.kafka_topic_name, 0, -1)
    assert len(events) == 1

    # Запускаем фоновую задачу для обработки очереди Redis
    await process_redis_queue(redis_client)

    # Проверяем, что очередь Redis пуста
    events = await redis_client.lrange(settings.kafka_topic_name, 0, -1)
    assert len(events) == 0
