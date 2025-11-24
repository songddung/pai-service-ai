from abc import ABC, abstractmethod
from typing import List
from domain.model.recommend_model import Festival

class EventPort(ABC):

    @abstractmethod
    def get_festivals(self, category: str, lat: float, lon: float) -> List[Festival]:
        pass
