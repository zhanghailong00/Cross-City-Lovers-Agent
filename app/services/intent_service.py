from __future__ import annotations

import re

from app.core.config import get_settings
from app.core.constants import DEFAULT_PREFERENCES
from app.domain.enums import DataMode, PriorityMode
from app.domain.models import Intent


class IntentService:
    """负责自然语言解析与约束标准化。"""

    def __init__(self) -> None:
        self.settings = get_settings()

    def parse_raw_query(self, raw_query: str) -> Intent:
        """从中文自然语言中提取最基础的结构化字段。"""
        origin_a = self._extract_city(raw_query, r"我在([^\s，,。；;]+)")
        origin_b = self._extract_city(raw_query, r"(?:她|他|对方)在([^\s，,。；;]+)")
        departure_date = self._extract_date(raw_query)
        days = self._extract_int(raw_query, r"(\d+)\s*天")
        budget = self._extract_int(raw_query, r"预算\s*(\d+)")
        preferences = [item for item in DEFAULT_PREFERENCES if item in raw_query]

        priority = PriorityMode.BALANCED
        if "省钱" in raw_query:
            priority = PriorityMode.COST_FIRST
        elif "省时" in raw_query or "快一点" in raw_query:
            priority = PriorityMode.TIME_FIRST
        elif "体验" in raw_query or "好玩" in raw_query:
            priority = PriorityMode.EXPERIENCE_FIRST

        return Intent(
            origin_a=origin_a,
            origin_b=origin_b,
            departure_date=departure_date,
            days=days,
            total_budget=budget,
            preferences=preferences,
            priority=priority,
            allow_transfer=False,
            transport_mode=["train"],
            data_mode=DataMode.ESTIMATED,
        )

    def normalize_intent(self, intent: Intent) -> tuple[Intent, list[str]]:
        """补默认值，并记录对用户透明的提示信息。"""
        warnings: list[str] = []

        if not intent.origin_a or not intent.origin_b:
            raise ValueError("请至少明确双方所在城市，例如：我在北京，她在杭州。")

        if intent.days is None:
            intent.days = self.settings.default_days
            warnings.append(f"未识别到游玩天数，已按默认 {intent.days} 天处理。")

        if intent.total_budget is None:
            intent.total_budget = self.settings.default_budget
            warnings.append(f"未识别到总预算，已按默认 {intent.total_budget} 元处理。")

        if not intent.departure_date:
            intent.data_mode = DataMode.ESTIMATED
            warnings.append("未识别到出发日期，当前输出将采用估算交通方案。")

        if not intent.preferences:
            intent.preferences = ["轻旅行"]
            warnings.append("未识别到偏好标签，已按轻旅行场景处理。")

        if not intent.priority:
            intent.priority = PriorityMode(self.settings.default_priority)

        return intent, warnings

    @staticmethod
    def _extract_city(raw_query: str, pattern: str) -> str | None:
        match = re.search(pattern, raw_query)
        return match.group(1) if match else None

    @staticmethod
    def _extract_date(raw_query: str) -> str | None:
        match = re.search(r"(20\d{2}-\d{2}-\d{2})", raw_query)
        return match.group(1) if match else None

    @staticmethod
    def _extract_int(raw_query: str, pattern: str) -> int | None:
        match = re.search(pattern, raw_query)
        return int(match.group(1)) if match else None

