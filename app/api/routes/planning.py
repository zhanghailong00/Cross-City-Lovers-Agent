from fastapi import APIRouter, HTTPException

from app.schemas.request import PlanningRequest
from app.schemas.response import PlanningResponse
from app.workflows.travel_meet_graph import TravelMeetWorkflow


router = APIRouter(prefix="/api/v1/plans", tags=["出行规划"])
workflow = TravelMeetWorkflow()


@router.post("/generate", response_model=PlanningResponse)
def generate_plan(request: PlanningRequest) -> PlanningResponse:
    """接收自然语言请求并返回结构化规划结果。"""
    try:
        state = workflow.invoke(request.raw_query)
        return PlanningResponse(
            success=True,
            message="规划生成成功",
            data=state["final_result"],
            warnings=state.get("warnings", []),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - 骨架阶段先保留统一兜底。
        raise HTTPException(status_code=500, detail=f"规划生成失败: {exc}") from exc

