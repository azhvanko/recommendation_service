import clickhouse_connect

from ..config import get_config, Config

__all__ = ("BaseService",)


class BaseService:
    config: Config
    clickhouse_client: clickhouse_connect.driver.AsyncClient

    def __init__(self, clickhouse_client: clickhouse_connect.driver.AsyncClient) -> None:
        self.config = get_config()
        self.clickhouse_client = clickhouse_client
