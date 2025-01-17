import asyncio

import pytest

from core.config import settings


@pytest.fixture(scope="session")
def event_loop() -> asyncio.AbstractEventLoop:
    """
    Создает и возвращает event loop для сессии тестов.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def set_test_mode():
    """
    Включает тестовый режим.
    """
    original_test_mode = settings.test_mode
    settings.test_mode = True
    yield
    settings.test_mode = original_test_mode
