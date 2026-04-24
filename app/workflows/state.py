from __future__ import annotations

from typing import TypedDict

from app.domain.models import CandidateCity, CityRecommendation, FinalRecommendationResult, Intent, PairedRoutePlan, TransportOption


class TravelMeetState(TypedDict, total=False):
    """定义 LangGraph 节点间共享的统一状态对象。"""

    raw_query: str
    intent: Intent
    normalized_intent: Intent
    candidate_cities: list[CandidateCity]
    transport_options_map: dict[str, dict[str, list[TransportOption]]]
    paired_route_plans: list[PairedRoutePlan]
    ranked_recommendations: list[CityRecommendation]
    top_result: CityRecommendation
    alternative_results: list[CityRecommendation]
    reasoning: list[str]
    notes: list[str]
    warnings: list[str]
    final_result: FinalRecommendationResult

