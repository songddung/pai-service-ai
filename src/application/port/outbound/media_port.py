from abc import ABC, abstractmethod
from typing import Optional
from domain.model.media_model import MediaInfo

class MediaPort(ABC):

    @abstractmethod
    async def get_media_info(self, media_id: str, token: Optional[str] = None) -> MediaInfo:
        """Get media information from media service"""
        pass
