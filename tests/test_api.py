import unittest
import warnings

from fastapi.testclient import TestClient

from app.api.main import app


warnings.filterwarnings(
    "ignore",
    message="The 'app' shortcut is now deprecated. Use the explicit style 'transport=WSGITransport\\(app=\\.\\.\\.\\)' instead.",
    category=DeprecationWarning,
)


class ApiTestCase(unittest.TestCase):
    """验证 API 层最小可用性。"""

    @classmethod
    def setUpClass(cls) -> None:
        """初始化测试客户端。"""
        cls.client = TestClient(app)

    def test_health_check_should_return_ok(self) -> None:
        """健康检查接口应返回正常状态。"""
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["app"], "Cross-City Lovers Agent")

    def test_generate_plan_should_return_recommendation(self) -> None:
        """规划接口应返回推荐城市与双边方案。"""
        response = self.client.post(
            "/api/v1/plans/generate",
            json={
                "raw_query": "我在北京，她在杭州，2026-05-01出发，玩3天，预算2000，想找个适合见面的城市"
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertIn("recommended_city", payload["data"])
        self.assertIn("best_plan", payload["data"])
        self.assertIn("reasoning", payload["data"])
        self.assertIn("display_text", payload["data"])
        self.assertIn("推荐城市", payload["data"]["display_text"])
