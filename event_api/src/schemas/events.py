from datetime import datetime
from typing import Generic, TypeVar

from pydantic import (
    BaseModel,
    Field,
    PrivateAttr,
    computed_field,
    field_validator,
)

T = TypeVar("T")


class BaseEvent(BaseModel):
    _event_type: str = PrivateAttr(default_factory=lambda: "base")
    _user_id: str | None = PrivateAttr(default_factory=lambda: "unauthorized")
    _user_role: str | None = PrivateAttr(default_factory=lambda: None)
    _user_verified: bool = PrivateAttr(default_factory=lambda: False)
    _ip_address: str | None = PrivateAttr(default_factory=lambda: None)
    _browser: str | None = PrivateAttr(default_factory=lambda: None)
    _operating_system: str | None = PrivateAttr(default_factory=lambda: None)
    timestamp: datetime
    device_id: str | None = None
    device_type: str | None = None
    country: str | None = None
    region: str | None = None
    city: str | None = None
    session_id: str | None = None
    session_start_time: datetime | None = None
    session_end_time: datetime | None = None
    extra_info: dict | None = None

    @computed_field
    @property
    def event_type(self) -> str:
        return self._event_type

    @computed_field
    @property
    def user_id(self) -> str:
        return self._user_id

    @computed_field
    @property
    def user_role(self) -> str:
        return self._user_role

    @computed_field
    @property
    def user_verified(self) -> bool:
        return self._user_verified

    @computed_field
    @property
    def ip_address(self) -> str:
        return self._ip_address

    @computed_field
    @property
    def browser(self) -> str:
        return self._browser

    @computed_field
    @property
    def operating_system(self) -> str:
        return self._operating_system

    @field_validator(
        "timestamp", "session_start_time", "session_end_time", mode="after"
    )
    @classmethod
    def remove_timezone(cls, value: datetime) -> datetime:
        """Удаление временной зоны для сохранения в ClickHouse"""
        return value.replace(tzinfo=None)


class SignUpEvent(BaseEvent):
    _event_type: str = PrivateAttr(default_factory=lambda: "sing up")
    email: str
    registration_method: str


class LoginEvent(BaseEvent):
    _event_type: str = PrivateAttr(default_factory=lambda: "login")
    login_method: str


class WatchMovieEvent(BaseEvent):
    _event_type: str = PrivateAttr(default_factory=lambda: "watch movie")
    movie_id: str
    movie_title: str
    genre: str
    duration: int
    watch_time: int


class PauseEvent(BaseEvent):
    _event_type: str = PrivateAttr(default_factory=lambda: "pause")
    movie_id: str
    movie_title: str
    pause_time: int


class ResumeEvent(BaseEvent):
    _event_type: str = PrivateAttr(default_factory=lambda: "resume")
    movie_id: str
    movie_title: str
    resume_time: int


class CompleteWatchEvent(BaseEvent):
    _event_type: str = PrivateAttr(default_factory=lambda: "complete watch")
    movie_id: str
    movie_title: str
    watch_duration: int


class SearchEvent(BaseEvent):
    _event_type: str = PrivateAttr(default_factory=lambda: "search")
    search_query: str
    results_count: int


class AddToFavoritesEvent(BaseEvent):
    _event_type: str = PrivateAttr(default_factory=lambda: "add to favorites")
    movie_id: str
    movie_title: str


class RemoveFromFavoritesEvent(BaseEvent):
    _event_type: str = PrivateAttr(default_factory=lambda: "remove from favorites")
    movie_id: str
    movie_title: str


class RateMovieEvent(BaseEvent):
    _event_type: str = PrivateAttr(default_factory=lambda: "rate movie")
    movie_id: str
    movie_title: str
    rating: int


class CommentOnMovieEvent(BaseEvent):
    _event_type: str = PrivateAttr(default_factory=lambda: "comments on movie")
    movie_id: str
    movie_title: str
    comment_text: str


class WatchTrailerEvent(BaseEvent):
    _event_type: str = PrivateAttr(default_factory=lambda: "watch trailer")
    movie_id: str
    movie_title: str
    trailer_duration: int


class ViewMovieDetailsEvent(BaseEvent):
    _event_type: str = PrivateAttr(default_factory=lambda: "view movie details")
    movie_id: str
    movie_title: str


class EventResult(BaseModel, Generic[T]):
    result: str = Field(default="Event received")
    event: T
