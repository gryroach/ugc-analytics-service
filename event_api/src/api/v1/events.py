from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from redis.asyncio import Redis

from db.redis import get_redis
from schemas.events import (
    AddToFavoritesEvent,
    CommentOnMovieEvent,
    CompleteWatchEvent,
    EventResult,
    LoginEvent,
    PauseEvent,
    RateMovieEvent,
    RemoveFromFavoritesEvent,
    ResumeEvent,
    SearchEvent,
    SignUpEvent,
    ViewMovieDetailsEvent,
    WatchMovieEvent,
    WatchTrailerEvent,
)
from services.events import process_event
from services.jwt_token import JWTBearer


router = APIRouter()

event_handlers = {
    "sign-up-event": SignUpEvent,
    "login-event": LoginEvent,
    "watch-movie-event": WatchMovieEvent,
    "pause-event": PauseEvent,
    "resume-event": ResumeEvent,
    "complete-watch-event": CompleteWatchEvent,
    "search-event": SearchEvent,
    "add-to-favorites-event": AddToFavoritesEvent,
    "remove-from-favorites-event": RemoveFromFavoritesEvent,
    "rate-movie-event": RateMovieEvent,
    "comments-on-movie-event": CommentOnMovieEvent,
    "watch-trailer-event": WatchTrailerEvent,
    "view-movie-details-event": ViewMovieDetailsEvent,
}


def create_event_route(
    event_model: type[BaseModel], response_model: type[BaseModel]
):  # noqa
    async def event_handler(
        event: event_model,
        request: Request,
        credentials: Annotated[dict, Depends(JWTBearer(auto_error=False))],
        redis: Annotated[Redis, Depends(get_redis)],
    ) -> BaseModel:
        processed_event = await process_event(event, request, credentials, redis)
        return response_model(event=processed_event)

    return event_handler


# Динамическое создание маршрутов для каждого типа события
for event_url, event_model in event_handlers.items():
    response_model = EventResult[event_model]
    router.post(f"/{event_url}", response_model=response_model)(
        create_event_route(event_model, response_model)
    )
