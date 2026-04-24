from enum import Enum


class DataMode(str, Enum):
    """描述交通数据来源模式。"""

    REAL = "real"
    HYBRID = "hybrid"
    ESTIMATED = "estimated"
    MOCK = "mock"


class PriorityMode(str, Enum):
    """描述用户更关注的优化方向。"""

    TIME_FIRST = "time_first"
    COST_FIRST = "cost_first"
    BALANCED = "balanced"
    EXPERIENCE_FIRST = "experience_first"

