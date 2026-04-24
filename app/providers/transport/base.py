from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.models import TransportOption


class BaseTransportProvider(ABC):
    """定义交通提供层的统一接口。"""

    @abstractmethod
    def get_options(
        self,
        origin: str,
        destination: str,
        date: str,
        from_station: str,
        to_station: str,
        role: str,
    ) -> list[TransportOption]:
        """获取指定城市对之间的候选交通方案列表。"""

