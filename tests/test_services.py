import unittest

from app.repositories.city_repository import CityRepository
from app.services.intent_service import IntentService
from app.services.transport_service import TransportService


class ServiceTestCase(unittest.TestCase):
    """验证基础服务层的关键行为。"""

    def setUp(self) -> None:
        """准备公共服务依赖。"""
        self.intent_service = IntentService()
        self.city_repository = CityRepository()
        self.transport_service = TransportService(self.city_repository)

    def test_intent_service_should_extract_core_fields(self) -> None:
        """自然语言应能提取双方城市、日期、预算和天数。"""
        intent = self.intent_service.parse_raw_query(
            "我在北京，她在杭州，2026-05-01出发，玩3天，预算2000，想吃点好吃的"
        )

        self.assertEqual(intent.origin_a, "北京")
        self.assertEqual(intent.origin_b, "杭州")
        self.assertEqual(intent.departure_date, "2026-05-01")
        self.assertEqual(intent.days, 3)
        self.assertEqual(intent.total_budget, 2000)

    def test_transport_service_should_return_options_map(self) -> None:
        """交通服务应为候选城市输出双方方案列表。"""
        intent = self.intent_service.parse_raw_query(
            "我在北京，她在杭州，2026-05-01出发，玩3天，预算2000"
        )
        intent, _ = self.intent_service.normalize_intent(intent)
        candidate_city = self.city_repository.get_city("南京")

        self.assertIsNotNone(candidate_city)

        options_map = self.transport_service.fetch_options(intent, [candidate_city])

        self.assertIn("南京", options_map)
        self.assertGreaterEqual(len(options_map["南京"]["from_a"]), 1)
        self.assertGreaterEqual(len(options_map["南京"]["from_b"]), 1)

