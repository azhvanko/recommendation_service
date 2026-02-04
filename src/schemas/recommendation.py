from pydantic import (
    BaseModel,
    Field,
)

__all__ = ("UserRecommendations",)


class UserRecommendations(BaseModel):
    uid: int = Field(...)
    products: list[int] = Field(...)
