import json
from typing import TypeVar

from fastapi import Request
from pydantic import BaseModel
from redis.asyncio import Redis
from user_agents import parse

from core.config import settings

T = TypeVar("T", bound=BaseModel)


def parse_request_data(request: Request) -> tuple[str, str, str]:
    """
    Парсинг данных из запроса.
    """
    ip_address = request.client.host
    user_agent = request.headers.get("User-Agent")
    try:
        parsed_user_agent = parse(user_agent)
    except TypeError:
        return "Unknown", "Other", "Other"
    browser = parsed_user_agent.browser.family
    operating_system = parsed_user_agent.os.family
    return ip_address, browser, operating_system


async def process_event(
    event: T,
    request: Request,
    credentials: dict,
    redis: Redis,
) -> T:
    """
    Обработка события.
    Добавление данных, полученных из декодированного токена и запроса с последующей записью события в очередь redis.
    """
    if credentials.get("auth_type") == "verified":
        event._user_id = credentials.get("user", None)
        event._user_role = credentials.get("role", None)
        event._user_verified = True

    ip_address, browser, operating_system = parse_request_data(request)
    event._ip_address = ip_address
    event._browser = browser
    event._operating_system = operating_system

    message = json.dumps(event.model_dump(), default=str)
    await redis.rpush(settings.kafka_topic_name, message)

    return event
