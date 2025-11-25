from abc import ABC, abstractmethod

class ImageFetchPort(ABC):

    @abstractmethod
    async def fetch_image_from_url(self, url: str) -> bytes:
        """Fetch image from URL and return as bytes"""
        pass
