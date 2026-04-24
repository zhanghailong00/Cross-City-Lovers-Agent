from __future__ import annotations

from app.domain.models import CandidateCity, CityRecommendation, PairedRoutePlan
from app.utils.score_utils import normalize_by_field


class ScoringService:
    """负责对候选城市进行最终综合评分。"""

    def score_candidates(
        self,
        paired_plans: list[PairedRoutePlan],
        candidate_cities: list[CandidateCity],
    ) -> list[CityRecommendation]:
        """将路线评分与城市属性评分合并，生成最终排序对象。"""
        if not paired_plans:
            return []

        city_map = {item.city_name: item for item in candidate_cities}
        route_scores = normalize_by_field([item.route_score for item in paired_plans])
        expense_scores = normalize_by_field(
            [city_map[item.target_city].expense_level for item in paired_plans]
        )
        tourism_scores = normalize_by_field(
            [city_map[item.target_city].tourism_score for item in paired_plans]
        )
        access_scores = normalize_by_field(
            [city_map[item.target_city].rail_hub_level for item in paired_plans]
        )

        recommendations: list[CityRecommendation] = []

        for index, paired_plan in enumerate(paired_plans):
            city = city_map[paired_plan.target_city]
            final_score = round(
                0.62 * route_scores[index]
                + 0.16 * expense_scores[index]
                - 0.14 * tourism_scores[index]
                - 0.08 * access_scores[index],
                4,
            )

            reason_tags: list[str] = []
            if paired_plan.wait_time_minutes <= 45:
                reason_tags.append("汇合等待短")
            if paired_plan.cost_total <= 700:
                reason_tags.append("交通预算友好")
            if city.tourism_score >= 8.5:
                reason_tags.append("城市体验较强")
            if city.rail_hub_level >= 9.0:
                reason_tags.append("高铁通达性好")

            recommendations.append(
                CityRecommendation(
                    city=city.city_name,
                    paired_plan=paired_plan,
                    city_expense_score=expense_scores[index],
                    city_experience_score=tourism_scores[index],
                    accessibility_score=access_scores[index],
                    final_score=final_score,
                    reason_tags=reason_tags,
                )
            )

        return recommendations

