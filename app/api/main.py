from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.planning import router as planning_router
from app.core.config import get_settings


settings = get_settings()

# 创建 FastAPI 应用实例。
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="异地情侣智能汇合出行规划系统第一版骨架",
)

app.include_router(health_router)
app.include_router(planning_router)

