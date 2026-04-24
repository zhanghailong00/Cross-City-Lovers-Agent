from __future__ import annotations

try:
    from langgraph.graph import END, START, StateGraph
except ModuleNotFoundError:  # pragma: no cover - 用于本地缺少 langgraph 时的兼容降级。
    END = "__end__"
    START = "__start__"
    StateGraph = None

from app.repositories.city_repository import CityRepository
from app.services.candidate_service import CandidateService
from app.services.intent_service import IntentService
from app.services.pairing_service import PairingService
from app.services.recommendation_service import RecommendationService
from app.services.scoring_service import ScoringService
from app.services.transport_service import TransportService
from app.workflows.state import TravelMeetState


class TravelMeetWorkflow:
    """封装旅行汇合规划主工作流。"""

    def __init__(self) -> None:
        self.city_repository = CityRepository()
        self.intent_service = IntentService()
        self.candidate_service = CandidateService(self.city_repository)
        self.transport_service = TransportService(self.city_repository)
        self.pairing_service = PairingService()
        self.scoring_service = ScoringService()
        self.recommendation_service = RecommendationService()
        self.graph = self._build_graph()

    def _build_graph(self):
        """构建第一版 LangGraph 线性工作流。"""
        if StateGraph is None:
            return None

        builder = StateGraph(TravelMeetState)
        builder.add_node("parse_intent", self._parse_intent)
        builder.add_node("normalize_constraints", self._normalize_constraints)
        builder.add_node("generate_candidate_cities", self._generate_candidate_cities)
        builder.add_node("fetch_transport_options", self._fetch_transport_options)
        builder.add_node("pair_routes", self._pair_routes)
        builder.add_node("score_candidates", self._score_candidates)
        builder.add_node("select_top_k", self._select_top_k)
        builder.add_node("generate_explanation", self._generate_explanation)
        builder.add_node("format_final_response", self._format_final_response)

        builder.add_edge(START, "parse_intent")
        builder.add_edge("parse_intent", "normalize_constraints")
        builder.add_edge("normalize_constraints", "generate_candidate_cities")
        builder.add_edge("generate_candidate_cities", "fetch_transport_options")
        builder.add_edge("fetch_transport_options", "pair_routes")
        builder.add_edge("pair_routes", "score_candidates")
        builder.add_edge("score_candidates", "select_top_k")
        builder.add_edge("select_top_k", "generate_explanation")
        builder.add_edge("generate_explanation", "format_final_response")
        builder.add_edge("format_final_response", END)

        return builder.compile()

    def invoke(self, raw_query: str) -> TravelMeetState:
        """执行工作流并返回完整状态。"""
        initial_state: TravelMeetState = {
            "raw_query": raw_query,
            "warnings": [],
            "reasoning": [],
            "notes": [],
        }
        if self.graph is None:
            return self._invoke_fallback(initial_state)
        return self.graph.invoke(initial_state)

    def _invoke_fallback(self, state: TravelMeetState) -> TravelMeetState:
        """在未安装 LangGraph 时，按相同顺序执行节点逻辑。"""
        state.update(self._parse_intent(state))
        state.update(self._normalize_constraints(state))
        state.update(self._generate_candidate_cities(state))
        state.update(self._fetch_transport_options(state))
        state.update(self._pair_routes(state))
        state.update(self._score_candidates(state))
        state.update(self._select_top_k(state))
        state.update(self._generate_explanation(state))
        state.update(self._format_final_response(state))
        return state

    def _parse_intent(self, state: TravelMeetState) -> dict:
        """节点一：解析自然语言意图。"""
        intent = self.intent_service.parse_raw_query(state["raw_query"])
        return {"intent": intent}

    def _normalize_constraints(self, state: TravelMeetState) -> dict:
        """节点二：补默认值并输出提示信息。"""
        normalized_intent, warnings = self.intent_service.normalize_intent(state["intent"])
        return {"normalized_intent": normalized_intent, "warnings": warnings}

    def _generate_candidate_cities(self, state: TravelMeetState) -> dict:
        """节点三：生成候选汇合城市。"""
        candidates = self.candidate_service.generate_candidates(state["normalized_intent"])
        return {"candidate_cities": candidates}

    def _fetch_transport_options(self, state: TravelMeetState) -> dict:
        """节点四：生成双方到候选城市的交通方案。"""
        options_map = self.transport_service.fetch_options(
            intent=state["normalized_intent"],
            candidate_cities=state["candidate_cities"],
        )
        return {"transport_options_map": options_map}

    def _pair_routes(self, state: TravelMeetState) -> dict:
        """节点五：为每个候选城市挑选最佳双边路线。"""
        normalized_intent = state["normalized_intent"]
        paired_plans = self.pairing_service.build_best_pairs(
            transport_options_map=state["transport_options_map"],
            travel_date=normalized_intent.departure_date or "待定日期",
            total_budget=normalized_intent.total_budget or 0,
        )
        return {"paired_route_plans": paired_plans}

    def _score_candidates(self, state: TravelMeetState) -> dict:
        """节点六：对候选城市进行综合评分。"""
        recommendations = self.scoring_service.score_candidates(
            paired_plans=state["paired_route_plans"],
            candidate_cities=state["candidate_cities"],
        )
        return {"ranked_recommendations": recommendations}

    def _select_top_k(self, state: TravelMeetState) -> dict:
        """节点七：选出主推荐与备选结果。"""
        top_result, alternatives = self.recommendation_service.select_top_k(
            state["ranked_recommendations"]
        )
        return {"top_result": top_result, "alternative_results": alternatives}

    def _generate_explanation(self, state: TravelMeetState) -> dict:
        """节点八：基于结构化结果生成解释文案。"""
        top_result = state["top_result"]
        reasoning = [
            f"推荐城市为{top_result.city}，该城市在当前候选中综合得分最高。",
            *[f"推荐理由：{tag}" for tag in top_result.reason_tags],
        ]
        notes = ["当前版本为第一版骨架，交通数据默认采用估算模式。", "当前结果未包含返程与住宿预算。"]
        return {"reasoning": reasoning, "notes": notes}

    def _format_final_response(self, state: TravelMeetState) -> dict:
        """节点九：封装最终输出结果。"""
        final_result = self.recommendation_service.build_final_result(
            top_result=state["top_result"],
            alternatives=state["alternative_results"],
            reasoning=state["reasoning"],
            notes=state["notes"],
        )
        return {"final_result": final_result}
