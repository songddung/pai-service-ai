from abc import ABC, abstractmethod

class ImageAnalysisPort(ABC):

    @abstractmethod
    def analyze_image(self, image_bytes: bytes) -> str:
        """Analyze image and return detected object label"""
        pass
