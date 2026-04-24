from pydantic import BaseModel, Field


class PlanningRequest(BaseModel):
    """规划请求体。"""

    raw_query: str = Field(..., min_length=2, description="用户自然语言输入")

