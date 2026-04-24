from __future__ import annotations

from ast import literal_eval
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - 兼容 Python 3.10 及以下版本。
    tomllib = None


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"


@dataclass(slots=True)
class AppSettings:
    """集中保存应用运行所需配置。"""

    app_name: str
    app_env: str
    host: str
    port: int
    default_days: int
    default_budget: int
    transport_budget_ratio: float
    default_priority: str
    default_data_mode: str
    llm_api_key: str | None = None
    llm_base_url: str | None = None
    llm_model: str | None = None


def _load_toml(path: Path) -> dict[str, Any]:
    """读取 TOML 文件，不存在时返回空字典。"""
    if not path.exists():
        return {}
    if tomllib is not None:
        with path.open("rb") as file:
            return tomllib.load(file)
    return _load_simple_toml(path)


def _load_simple_toml(path: Path) -> dict[str, Any]:
    """在缺少 TOML 解析库时，使用简化解析逻辑读取当前项目配置。"""
    result: dict[str, Any] = {}
    current_section: dict[str, Any] | None = None

    with path.open("r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("[") and line.endswith("]"):
                section_name = line[1:-1].strip()
                result[section_name] = {}
                current_section = result[section_name]
                continue

            if "=" not in line or current_section is None:
                continue

            key, value = [item.strip() for item in line.split("=", 1)]
            current_section[key] = _parse_scalar(value)

    return result


def _parse_scalar(value: str) -> Any:
    """解析当前项目中用到的字符串、数字和布尔量。"""
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"

    try:
        return literal_eval(value)
    except (ValueError, SyntaxError):
        return value.strip('"').strip("'")


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """加载公共配置和本地敏感配置。"""
    settings_data = _load_toml(CONFIG_DIR / "settings.toml")
    secrets_data = _load_toml(CONFIG_DIR / "secrets.toml")

    app_config = settings_data.get("app", {})
    planner_config = settings_data.get("planner", {})
    llm_config = secrets_data.get("llm", {})

    return AppSettings(
        app_name=app_config.get("name", "Cross-City Lovers Agent"),
        app_env=app_config.get("env", "dev"),
        host=app_config.get("host", "127.0.0.1"),
        port=int(app_config.get("port", 8000)),
        default_days=int(planner_config.get("default_days", 2)),
        default_budget=int(planner_config.get("default_budget", 3000)),
        transport_budget_ratio=float(planner_config.get("transport_budget_ratio", 0.35)),
        default_priority=planner_config.get("default_priority", "balanced"),
        default_data_mode=planner_config.get("default_data_mode", "estimated"),
        llm_api_key=llm_config.get("api_key"),
        llm_base_url=llm_config.get("base_url"),
        llm_model=llm_config.get("model"),
    )
