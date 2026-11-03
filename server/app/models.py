from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

Failure = Literal["blocked", "unavailable", "parse_error"]
Status = Literal["ok", "partial", "stale", "blocked", "unavailable", "parse_error"]


class Model(BaseModel):
    model_config = ConfigDict(
        frozen=True, alias_generator=to_camel, populate_by_name=True, extra="forbid"
    )


class Board(Model):
    id: str
    name: str
    metric_label: str


class Category(Model):
    id: str
    name: str
    group: str
    board_ids: tuple[str, ...]


class Source(Model):
    id: str
    name: str
    home_url: str
    note: str
    categories: tuple[Category, ...]
    boards: tuple[Board, ...]


class Catalog(Model):
    sources: tuple[Source, ...]


class Book(Model):
    rank: int = Field(ge=1, le=10)
    id: str
    title: str | None
    author: str | None
    url: str
    metric: str | None = None
    genre: str | None = None
    metadata_status: Literal["complete", "partial"] = "complete"


class RankingSnapshot(Model):
    source_id: str
    category_id: str
    board_id: str
    status: Status
    message: str
    source_url: str
    fetched_at: datetime
    source_updated_at: datetime | None = None
    from_cache: bool = False
    failure_reason: Failure | None = None
    books: tuple[Book, ...] = Field(default=(), max_length=10)


class Health(Model):
    status: Literal["ok"] = "ok"


class ErrorDetail(Model):
    code: Literal["INVALID_SELECTION"] = "INVALID_SELECTION"
    message: str


class SelectionError(Model):
    detail: ErrorDetail
