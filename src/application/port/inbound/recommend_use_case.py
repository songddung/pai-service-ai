from abc import ABC, abstractmethod
from domain.model.recommend_model import RecommendRequest, RecommendResponse

class RecommendUseCase(ABC):

    @abstractmethod
    def recommend_event(self, req: RecommendRequest) -> RecommendResponse:
        pass
