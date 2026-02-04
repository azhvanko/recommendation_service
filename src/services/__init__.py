import clickhouse_connect
from fastapi import Depends

from ..clickhouse import get_clickhouse_async_client
from .recommendation import RecommendationService

__all__ = (
    "get_recommendation_service",
    "RecommendationService",
)


def get_recommendation_service(
    clickhouse_client: clickhouse_connect.driver.AsyncClient = Depends(get_clickhouse_async_client)
) -> RecommendationService:
    return RecommendationService(clickhouse_client)
