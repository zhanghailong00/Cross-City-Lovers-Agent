from __future__ import annotations

from app.domain.models import CityRecommendation, FinalRecommendationResult


class RecommendationService:
    """负责 Top-K 选择、最终结果封装和展示文本生成。"""

    def select_top_k(
        self, recommendations: list[CityRecommendation], top_k: int = 4
    ) -> tuple[CityRecommendation, list[CityRecommendation]]:
        """选出主推荐和备选推荐。"""
        if not recommendations:
            raise ValueError("当前条件下未找到可用的汇合方案。")

        ranked = sorted(recommendations, key=lambda item: item.final_score)
        for index, item in enumerate(ranked, start=1):
            item.rank = index

        top_result = ranked[0]
        alternatives = ranked[1:top_k]
        return top_result, alternatives

    def build_final_result(
        self,
        top_result: CityRecommendation,
        alternatives: list[CityRecommendation],
        reasoning: list[str],
        notes: list[str],
    ) -> FinalRecommendationResult:
        """封装最终输出对象，供 API 层直接返回。"""
        return FinalRecommendationResult(
            recommended_city=top_result.city,
            alternatives=[item.city for item in alternatives],
            best_plan=top_result.paired_plan,
            other_plans=alternatives,
            reasoning=reasoning,
            notes=notes,
            display_text=self.build_display_text(
                top_result=top_result,
                alternatives=alternatives,
                reasoning=reasoning,
                notes=notes,
            ),
        )

    def build_display_text(
        self,
        top_result: CityRecommendation,
        alternatives: list[CityRecommendation],
        reasoning: list[str],
        notes: list[str],
    ) -> str:
        """把结构化结果渲染为更接近产品输出的中文展示文本。"""
        best_plan = top_result.paired_plan
        plan_a = best_plan.option_a
        plan_b = best_plan.option_b

        lines: list[str] = [
            f"📍 推荐城市：{top_result.city}",
            "",
            f"🏙️ 备选城市：{self._join_city_names([item.city for item in alternatives])}",
            "",
            "🚄 出行方案：",
            "",
            f"【{plan_a.from_city} → {plan_a.to_city}】",
            f"日期：{plan_a.date}",
            f"车次：{plan_a.train_no}",
            f"出发站：{plan_a.from_station}",
            f"出发时间：{plan_a.depart_time}",
            f"到达站：{plan_a.to_station}",
            f"到达时间：{plan_a.arrive_time}",
            f"交通方式：{plan_a.transport_type}",
            "",
            f"【{plan_b.from_city} → {plan_b.to_city}】",
            f"日期：{plan_b.date}",
            f"车次：{plan_b.train_no}",
            f"出发站：{plan_b.from_station}",
            f"出发时间：{plan_b.depart_time}",
            f"到达站：{plan_b.to_station}",
            f"到达时间：{plan_b.arrive_time}",
            f"交通方式：{plan_b.transport_type}",
            "",
            f"🎯 汇合时间：{best_plan.meet_time} {best_plan.meet_station}",
            f"💰 预计交通总费用：{self._format_price(best_plan.cost_total)}元",
            "",
            "💡 推荐理由：",
        ]

        lines.extend([f"- {item}" for item in reasoning])

        if notes:
            lines.extend(["", "📝 提示："])
            lines.extend([f"- {item}" for item in notes])

        return "\n".join(lines)

    @staticmethod
    def _join_city_names(city_names: list[str]) -> str:
        """把城市列表格式化为展示文本。"""
        if not city_names:
            return "暂无"
        return "、".join(city_names)

    @staticmethod
    def _format_price(price: float) -> str:
        """把价格格式化为更自然的中文展示形式。"""
        if float(price).is_integer():
            return str(int(price))
        return f"{price:.2f}"
