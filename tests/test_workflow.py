import unittest

from app.workflows.travel_meet_graph import TravelMeetWorkflow


class WorkflowTestCase(unittest.TestCase):
    """验证主工作流在骨架阶段可以稳定输出关键字段。"""

    def setUp(self) -> None:
        """为每个测试准备一个新的工作流实例。"""
        self.workflow = TravelMeetWorkflow()

    def test_workflow_should_generate_final_result(self) -> None:
        """标准输入应生成最终推荐结果。"""
        state = self.workflow.invoke(
            "我在北京，她在杭州，2026-05-01出发，玩3天，预算2000，想找一个适合约会的城市"
        )

        self.assertIn("final_result", state)
        final_result = state["final_result"]
        data = final_result.model_dump() if hasattr(final_result, "model_dump") else final_result.dict()

        self.assertIn(data["recommended_city"], ["南京", "合肥", "苏州", "武汉"])
        self.assertGreaterEqual(len(data["reasoning"]), 1)
        self.assertIn("best_plan", data)
        self.assertIn("alternatives", data)
        self.assertIn("display_text", data)
        self.assertIn("出行方案", data["display_text"])

    def test_workflow_should_add_warning_when_date_missing(self) -> None:
        """缺少日期时应给出估算模式提示。"""
        state = self.workflow.invoke("我在北京，她在杭州，预算2000，想找个中间城市玩3天")

        warnings = state.get("warnings", [])
        self.assertTrue(any("估算交通方案" in item for item in warnings))
