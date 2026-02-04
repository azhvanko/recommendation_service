import clickhouse_connect

__all__ = ("BaseService",)


class BaseService:
    clickhouse_client: clickhouse_connect.driver.AsyncClient

    def __init__(self, clickhouse_client: clickhouse_connect.driver.AsyncClient) -> None:
        self.clickhouse_client = clickhouse_client
