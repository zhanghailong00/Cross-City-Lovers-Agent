DEFAULT_PREFERENCES = [
    "美食",
    "散步",
    "拍照",
    "夜景",
    "古都",
    "自然",
    "轻旅行",
]

MAX_SINGLE_TRAVEL_HOURS = 8.0
MAX_WAIT_MINUTES = 120
MAX_TRANSPORT_BUDGET_MULTIPLIER = 1.3


PAIR_CANDIDATE_HINTS: dict[str, list[str]] = {
    "北京|杭州": ["南京", "合肥", "武汉", "苏州"],
    "广州|武汉": ["长沙", "南昌", "武汉"],
}

