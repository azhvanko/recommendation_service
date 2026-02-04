from functools import cache

from pydantic import (
    ClickHouseDsn,
    Field,
)
from pydantic_settings import BaseSettings

__all__ = (
    "Config",
    "get_config",
)


class Config(BaseSettings):
    # Project
    debug: bool = Field(default=False)
    # ClickHouse
    clickhouse_dsn: ClickHouseDsn = Field(...)


@cache
def get_config() -> Config:
    return Config()
