def normalize_by_field(values: list[float]) -> list[float]:
    """将一组数值做最小-最大归一化。"""
    if not values:
        return []

    min_value = min(values)
    max_value = max(values)

    if min_value == max_value:
        return [0.0 for _ in values]

    return [round((value - min_value) / (max_value - min_value), 4) for value in values]

