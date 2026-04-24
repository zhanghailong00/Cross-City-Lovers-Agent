from __future__ import annotations

from datetime import datetime, timedelta


def _parse_time(value: str) -> datetime:
    """将 HH:MM 文本解析为时间对象。"""
    return datetime.strptime(value, "%H:%M")


def add_hours_to_time(start_time: str, hours: float) -> str:
    """在指定时间上增加若干小时，并返回 HH:MM。"""
    start = _parse_time(start_time)
    end = start + timedelta(hours=hours)
    return end.strftime("%H:%M")


def minutes_between(left: str, right: str) -> int:
    """计算两个时间字符串之间的分钟差。"""
    left_dt = _parse_time(left)
    right_dt = _parse_time(right)
    return int((left_dt - right_dt).total_seconds() // 60)


def to_datetime_string(date_text: str, time_text: str) -> str:
    """将日期和时间拼接为统一展示格式。"""
    return f"{date_text} {time_text}"

