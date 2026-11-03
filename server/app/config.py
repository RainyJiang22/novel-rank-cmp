import os

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    request_timeout: float = Field(default=10, gt=0, le=60)
    query_timeout: float = Field(default=40, gt=0, le=120)
    concurrency: int = Field(default=4, ge=1, le=16)
    source_interval: float = Field(default=0.5, ge=0, le=60)
    cache_ttl: float = Field(default=900, gt=0, le=86400)
    stale_ttl: float = Field(default=86400, gt=0, le=86400)
    retry_interval: float = Field(default=60, gt=0, le=3600)
    max_response_bytes: int = Field(default=3_000_000, ge=1024, le=10_000_000)

    @model_validator(mode="after")
    def check_ttls(self):
        if self.stale_ttl < self.cache_ttl:
            raise ValueError("stale_ttl must be >= cache_ttl")
        return self

    @classmethod
    def from_env(cls):
        # No automatic .env loading: personal settings never become repository inputs.
        return cls(**{
            name: os.environ[f"NOVELRANK_{name.upper()}"]
            for name in cls.model_fields
            if f"NOVELRANK_{name.upper()}" in os.environ
        })
