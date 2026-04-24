from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.enums import DataMode, PriorityMode


class Intent(BaseModel):
    """结构化用户意图对象。"""

    origin_a: str | None = None
    origin_b: str | None = None
    departure_date: str | None = None
    days: int | None = None
    total_budget: int | None = None
    preferences: list[str] = Field(default_factory=list)
    priority: PriorityMode = PriorityMode.BALANCED
    allow_transfer: bool = False
    transport_mode: list[str] = Field(default_factory=lambda: ["train"])
    data_mode: DataMode = DataMode.ESTIMATED


class CandidateCity(BaseModel):
    """候选汇合城市对象。"""

    city_name: str
    province: str
    city_tier: int
    rail_hub_level: float
    default_station: str
    is_popular_destination: bool = True
    tourism_score: float = 0.0
    expense_level: float = 0.0
    tags: list[str] = Field(default_factory=list)


class TransportOption(BaseModel):
    """单条交通方案对象。"""

    from_city: str
    to_city: str
    date: str
    transport_type: str
    train_no: str
    from_station: str
    to_station: str
    depart_time: str
    arrive_time: str
    duration_hours: float
    price: float
    is_direct: bool = True
    data_source_level: str = "estimated"


class PairedRoutePlan(BaseModel):
    """某个候选城市下的双边交通组合。"""

    target_city: str
    option_a: TransportOption
    option_b: TransportOption
    meet_station: str
    meet_time: str
    wait_time_minutes: int
    time_total_hours: float
    cost_total: float
    time_gap_hours: float
    cost_gap: float
    route_score: float
    budget_penalty: float
    fairness_score: float


class CityRecommendation(BaseModel):
    """城市级排序结果对象。"""

    city: str
    paired_plan: PairedRoutePlan
    city_expense_score: float
    city_experience_score: float
    accessibility_score: float
    final_score: float
    rank: int = 0
    reason_tags: list[str] = Field(default_factory=list)


class FinalRecommendationResult(BaseModel):
    """最终返回给前端的结果对象。"""

    recommended_city: str
    alternatives: list[str]
    best_plan: PairedRoutePlan
    other_plans: list[CityRecommendation]
    reasoning: list[str]
    notes: list[str]
    display_text: str
