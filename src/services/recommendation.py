import logging

from fastapi import status

from ..exceptions import HTTPException
from ..schemas.recommendation import UserRecommendations
from .base import BaseService

__all__ = ("RecommendationService",)

logger = logging.getLogger(__name__)

PERSONAL_RECOMMENDATIONS_QUERY_TEMPLATE = """
    SELECT
        t.pid
    FROM (
        SELECT
            pid,
            brand,
            sum(click * 1 + add_to_cart * 3) AS score,
            row_number() OVER (
                PARTITION BY brand 
                ORDER BY sum(click * 1 + add_to_cart * 3) DESC
            ) AS rn
        FROM
            {db_table:Identifier}
        WHERE
            uid = {uid:UInt64}
        GROUP BY
            pid,
            brand
        HAVING
            sum(purchase) = 0
    ) t
    WHERE
        t.rn <= {max_items_per_brand:UInt8}
    ORDER BY
        t.score DESC
    LIMIT {total_limit:UInt8}
"""
GLOBAL_RECOMMENDATIONS_QUERY_TEMPLATE = """
    SELECT
        t.pid
    FROM (
        SELECT
            pid,
            brand,
            sum(click * 1 + add_to_cart * 3 + purchase * 5) AS score,
            row_number() OVER (
                PARTITION BY brand 
                ORDER BY sum(click * 1 + add_to_cart * 3 + purchase * 5) DESC
            ) AS rn
        FROM
            {db_table:Identifier}
        GROUP BY
            pid,
            brand
    ) t
    WHERE
        t.rn <= {max_items_per_brand:UInt8}
    ORDER BY
        t.score DESC
    LIMIT {total_limit:UInt8}
"""
USER_EVENTS_TABLE = "user_events"
MAX_ITEMS_PER_BRAND = 2
TOTAL_RECOMMENDATIONS_LIMIT = 5


class RecommendationService(BaseService):
    async def get_recommendations(self, user_id: int) -> UserRecommendations:
        try:
            query_result = await self.clickhouse_client.query(
                PERSONAL_RECOMMENDATIONS_QUERY_TEMPLATE,
                parameters={
                    "db_table": USER_EVENTS_TABLE,
                    "uid": user_id,
                    "max_items_per_brand": MAX_ITEMS_PER_BRAND,
                    "total_limit": TOTAL_RECOMMENDATIONS_LIMIT,
                },
            )
            products = [row[0] for row in query_result.result_rows]
            if not products:
                # TODO: clarify logic: should existing users with no matching items receive global top or an empty list?
                query_result = await self.clickhouse_client.query(
                    GLOBAL_RECOMMENDATIONS_QUERY_TEMPLATE,
                    parameters={
                        "db_table": USER_EVENTS_TABLE,
                        "max_items_per_brand": MAX_ITEMS_PER_BRAND,
                        "total_limit": TOTAL_RECOMMENDATIONS_LIMIT,
                    },
                )
                products = [row[0] for row in query_result.result_rows]
        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}", exc_info=True)
            raise HTTPException(
                detail="Failed to get recommendations",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return UserRecommendations(uid=user_id, products=products)
