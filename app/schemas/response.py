from pydantic import BaseModel, Field

from app.domain.models import FinalRecommendationResult


class PlanningResponse(BaseModel):
    """规划响应体。"""

    success: bool
    message: str
    data: FinalRecommendationResult | None = None
    warnings: list[str] = Field(default_factory=list)

