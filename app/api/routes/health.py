from fastapi import APIRouter

from app.core.config import get_settings


router = APIRouter(tags=["系统"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """提供最小健康检查接口，便于联调和部署验证。"""
    settings = get_settings()
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}

