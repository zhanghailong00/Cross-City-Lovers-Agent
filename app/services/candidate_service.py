from __future__ import annotations

from app.core.constants import PAIR_CANDIDATE_HINTS
from app.domain.models import CandidateCity, Intent
from app.repositories.city_repository import CityRepository


class CandidateService:
    """负责生成和过滤候选汇合城市。"""

    def __init__(self, city_repository: CityRepository) -> None:
        self.city_repository = city_repository

    @staticmethod
    def _build_pair_key(city_a: str, city_b: str) -> str:
        return "|".join(sorted([city_a, city_b]))

    def generate_candidates(self, intent: Intent) -> list[CandidateCity]:
        """优先使用候选提示，其次按热门城市兜底。"""
        if not intent.origin_a or not intent.origin_b:
            raise ValueError("缺少双方出发城市，无法生成候选城市。")

        pair_key = self._build_pair_key(intent.origin_a, intent.origin_b)
        direct_key = f"{intent.origin_a}|{intent.origin_b}"
        reverse_key = f"{intent.origin_b}|{intent.origin_a}"
        hinted_names = (
            PAIR_CANDIDATE_HINTS.get(direct_key)
            or PAIR_CANDIDATE_HINTS.get(reverse_key)
            or PAIR_CANDIDATE_HINTS.get(pair_key, [])
        )

        excluded = {intent.origin_a, intent.origin_b}
        candidates: list[CandidateCity] = []

        for name in hinted_names:
            city = self.city_repository.get_city(name)
            if city and city.city_name not in excluded:
                candidates.append(city)

        if candidates:
            return candidates[:5]

        popular_cities = sorted(
            self.city_repository.list_all_cities(),
            key=lambda item: (item.rail_hub_level + item.tourism_score),
            reverse=True,
        )

        for city in popular_cities:
            if city.city_name not in excluded:
                candidates.append(city)
            if len(candidates) >= 5:
                break

        return candidates
