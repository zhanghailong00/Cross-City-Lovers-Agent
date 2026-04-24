from __future__ import annotations

from app.core.config import get_settings
from app.core.constants import (
    MAX_SINGLE_TRAVEL_HOURS,
    MAX_TRANSPORT_BUDGET_MULTIPLIER,
    MAX_WAIT_MINUTES,
)
from app.domain.models import PairedRoutePlan, TransportOption
from app.utils.time_utils import minutes_between, to_datetime_string


class PairingService:
    """负责为每个候选城市找出最优双人路线组合。"""

    def __init__(self) -> None:
        self.settings = get_settings()

    def build_best_pairs(
        self,
        transport_options_map: dict[str, dict[str, list[TransportOption]]],
        travel_date: str,
        total_budget: int,
    ) -> list[PairedRoutePlan]:
        """遍历每个城市的双边路线组合，并选出该城市最优组合。"""
        transport_budget_cap = total_budget * self.settings.transport_budget_ratio
        paired_plans: list[PairedRoutePlan] = []

        for city_name, option_group in transport_options_map.items():
            best_plan: PairedRoutePlan | None = None

            for option_a in option_group.get("from_a", []):
                for option_b in option_group.get("from_b", []):
                    candidate = self._build_pair_plan(
                        city_name=city_name,
                        option_a=option_a,
                        option_b=option_b,
                        travel_date=travel_date,
                        transport_budget_cap=transport_budget_cap,
                    )
                    if candidate is None:
                        continue

                    if best_plan is None or candidate.route_score < best_plan.route_score:
                        best_plan = candidate

            if best_plan is not None:
                paired_plans.append(best_plan)

        return paired_plans

    def _build_pair_plan(
        self,
        city_name: str,
        option_a: TransportOption,
        option_b: TransportOption,
        travel_date: str,
        transport_budget_cap: float,
    ) -> PairedRoutePlan | None:
        """构建并校验一个双边路线组合。"""
        if option_a.duration_hours > MAX_SINGLE_TRAVEL_HOURS:
            return None
        if option_b.duration_hours > MAX_SINGLE_TRAVEL_HOURS:
            return None

        wait_time = abs(minutes_between(option_a.arrive_time, option_b.arrive_time))
        if wait_time > MAX_WAIT_MINUTES:
            return None

        cost_total = round(option_a.price + option_b.price, 2)
        if cost_total > transport_budget_cap * MAX_TRANSPORT_BUDGET_MULTIPLIER:
            return None

        time_total = round(option_a.duration_hours + option_b.duration_hours, 2)
        time_gap = round(abs(option_a.duration_hours - option_b.duration_hours), 2)
        cost_gap = round(abs(option_a.price - option_b.price), 2)
        fairness_score = round(0.7 * time_gap + 0.3 * (cost_gap / max(transport_budget_cap, 1.0)), 4)
        budget_penalty = self._calculate_budget_penalty(cost_total, transport_budget_cap)

        route_score = round(
            0.30 * (time_total / 12.0)
            + 0.28 * (cost_total / max(transport_budget_cap, 1.0))
            + 0.20 * (time_gap / 6.0)
            + 0.10 * (cost_gap / max(transport_budget_cap, 1.0))
            + 0.12 * (wait_time / MAX_WAIT_MINUTES)
            + budget_penalty,
            4,
        )

        meet_time = max(option_a.arrive_time, option_b.arrive_time)

        return PairedRoutePlan(
            target_city=city_name,
            option_a=option_a,
            option_b=option_b,
            meet_station=option_a.to_station,
            meet_time=to_datetime_string(travel_date, meet_time),
            wait_time_minutes=wait_time,
            time_total_hours=time_total,
            cost_total=cost_total,
            time_gap_hours=time_gap,
            cost_gap=cost_gap,
            route_score=route_score,
            budget_penalty=budget_penalty,
            fairness_score=fairness_score,
        )

    @staticmethod
    def _calculate_budget_penalty(cost_total: float, transport_budget_cap: float) -> float:
        """按超预算程度施加强惩罚。"""
        if cost_total <= transport_budget_cap:
            return 0.0
        if cost_total <= transport_budget_cap * 1.1:
            return 0.15
        if cost_total <= transport_budget_cap * 1.25:
            return 0.35
        return 0.70

