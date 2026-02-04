import typing as t

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)

from ...schemas.recommendation import UserRecommendations
from ...services import (
    get_recommendation_service,
    RecommendationService,
)
from ..responses import VALIDATION_ERROR_RESPONSE

USER_ID_QUERY = t.Annotated[
    int,
    Query(
        ...,
        ge=1,
        description="User uid",
        examples=[100],
        alias="user_id",
    ),
]
recommendations_router = APIRouter(prefix="/recommendations", tags=["recommendations",],)


@recommendations_router.get(
    "",
    response_model=UserRecommendations,
    responses=VALIDATION_ERROR_RESPONSE,
    status_code=status.HTTP_200_OK,
)
async def get_recommendations(
    user_id: USER_ID_QUERY,
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
) -> UserRecommendations:
    return await recommendation_service.get_recommendations(user_id)
