from fastapi import APIRouter, Depends
from application.service.recommend_service import RecommendService
from application.port.inbound.recommend_use_case import RecommendUseCase
from domain.model.recommend_model import RecommendRequest, RecommendResponse

recommend_router = APIRouter()

def get_recommend_service() -> RecommendUseCase:
    return RecommendService()

@recommend_router.post("/", response_model=RecommendResponse)
def recommend_event(req: RecommendRequest, recommend_service: RecommendUseCase = Depends(get_recommend_service)):
    return recommend_service.recommend_event(req)
