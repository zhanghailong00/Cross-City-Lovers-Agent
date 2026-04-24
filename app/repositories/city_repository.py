from __future__ import annotations

import json
from pathlib import Path

from app.domain.models import CandidateCity


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class CityRepository:
    """读取并组合城市基础信息与画像数据。"""

    def __init__(self) -> None:
        self.city_master_path = PROJECT_ROOT / "data" / "cities" / "city_master.json"
        self.city_profiles_path = PROJECT_ROOT / "data" / "profiles" / "city_profiles.json"
        self.rail_access_seed_path = PROJECT_ROOT / "data" / "transport" / "rail_access_seed.json"
        self._city_master = self._load_json(self.city_master_path)
        self._city_profiles = self._load_json(self.city_profiles_path)
        self._rail_access_seed = self._load_json(self.rail_access_seed_path)

    @staticmethod
    def _load_json(path: Path) -> dict | list:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def get_city(self, city_name: str) -> CandidateCity | None:
        """按城市名查询组合后的城市对象。"""
        for item in self._city_master:
            aliases = item.get("aliases", [])
            if city_name == item["city_name"] or city_name in aliases:
                profile = self._city_profiles.get(item["city_name"], {})
                return CandidateCity(
                    city_name=item["city_name"],
                    province=item["province"],
                    city_tier=item["city_tier"],
                    rail_hub_level=item["rail_hub_level"],
                    default_station=item["default_station"],
                    is_popular_destination=item.get("is_popular_destination", True),
                    tourism_score=profile.get("tourism_score", 0.0),
                    expense_level=profile.get("expense_level", 0.0),
                    tags=profile.get("tags", []),
                )
        return None

    def list_all_cities(self) -> list[CandidateCity]:
        """返回全部可用城市。"""
        cities: list[CandidateCity] = []
        for item in self._city_master:
            city = self.get_city(item["city_name"])
            if city is not None:
                cities.append(city)
        return cities

    def get_station_name(self, city_name: str) -> str:
        """返回城市默认车站名称。"""
        city = self.get_city(city_name)
        if city is None:
            raise ValueError(f"未找到城市站点信息: {city_name}")
        return city.default_station

    def get_rail_access_seed(self) -> dict[str, dict[str, float]]:
        """返回高铁估算种子数据。"""
        return self._rail_access_seed

