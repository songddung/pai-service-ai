from fastapi import APIRouter, Depends
from application.port.inbound.recommend_use_case import RecommendUseCase
from domain.model.recommend_model import RecommendRequest, RecommendResponse
from adapter.inbound.web.dependencies import get_recommend_service

recommend_router = APIRouter()

@recommend_router.post("/", response_model=RecommendResponse)
def recommend_event(req: RecommendRequest, recommend_service: RecommendUseCase = Depends(get_recommend_service)):
    return recommend_service.recommend_event(req)
