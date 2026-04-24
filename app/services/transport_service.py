from __future__ import annotations

from app.domain.models import CandidateCity, Intent, TransportOption
from app.providers.transport.estimated_provider import EstimatedTransportProvider
from app.repositories.city_repository import CityRepository


class TransportService:
    """统一封装交通方案获取逻辑。"""

    def __init__(self, city_repository: CityRepository) -> None:
        self.city_repository = city_repository
        self.provider = EstimatedTransportProvider(city_repository.get_rail_access_seed())

    def fetch_options(
        self,
        intent: Intent,
        candidate_cities: list[CandidateCity],
    ) -> dict[str, dict[str, list[TransportOption]]]:
        """为每个候选城市抓取双方的候选交通方案。"""
        if not intent.origin_a or not intent.origin_b:
            raise ValueError("缺少出发城市，无法获取交通方案。")

        travel_date = intent.departure_date or "待定日期"
        options_map: dict[str, dict[str, list[TransportOption]]] = {}

        for city in candidate_cities:
            options_map[city.city_name] = {
                "from_a": self.provider.get_options(
                    origin=intent.origin_a,
                    destination=city.city_name,
                    date=travel_date,
                    from_station=self.city_repository.get_station_name(intent.origin_a),
                    to_station=city.default_station,
                    role="a",
                ),
                "from_b": self.provider.get_options(
                    origin=intent.origin_b,
                    destination=city.city_name,
                    date=travel_date,
                    from_station=self.city_repository.get_station_name(intent.origin_b),
                    to_station=city.default_station,
                    role="b",
                ),
            }

        return options_map

