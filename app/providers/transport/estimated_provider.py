from __future__ import annotations

from app.domain.models import TransportOption
from app.providers.transport.base import BaseTransportProvider
from app.utils.time_utils import add_hours_to_time


class EstimatedTransportProvider(BaseTransportProvider):
    """基于种子数据和简单规则生成估算交通方案。"""

    def __init__(self, access_seed: dict[str, dict[str, float]]):
        self.access_seed = access_seed

    def get_options(
        self,
        origin: str,
        destination: str,
        date: str,
        from_station: str,
        to_station: str,
        role: str,
    ) -> list[TransportOption]:
        direct_key = f"{origin}|{destination}"
        reverse_key = f"{destination}|{origin}"
        pair_key = "|".join(sorted([origin, destination]))
        seed = (
            self.access_seed.get(direct_key)
            or self.access_seed.get(reverse_key)
            or self.access_seed.get(pair_key)
            or {"duration_hours": 5.0, "price": 320}
        )

        base_departures = ["08:00", "09:00"] if role == "a" else ["09:10", "10:10"]
        options: list[TransportOption] = []

        for index, depart_time in enumerate(base_departures, start=1):
            duration = round(float(seed["duration_hours"]) + (index - 1) * 0.2, 1)
            price = round(float(seed["price"]) + (index - 1) * 20, 2)
            train_no = f"G{abs(hash((origin, destination, index))) % 9000 + 1000}"

            options.append(
                TransportOption(
                    from_city=origin,
                    to_city=destination,
                    date=date,
                    transport_type="高铁",
                    train_no=train_no,
                    from_station=from_station,
                    to_station=to_station,
                    depart_time=depart_time,
                    arrive_time=add_hours_to_time(depart_time, duration),
                    duration_hours=duration,
                    price=price,
                    is_direct=True,
                    data_source_level="estimated",
                )
            )

        return options
