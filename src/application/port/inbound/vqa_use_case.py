from abc import ABC, abstractmethod
from domain.model.vqa_model import VQARequest, VQAResponse

class VQAUseCase(ABC):

    @abstractmethod
    async def handle_vqa(self, request: VQARequest) -> VQAResponse:
        pass
