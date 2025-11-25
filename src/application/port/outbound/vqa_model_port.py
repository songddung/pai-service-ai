from abc import ABC, abstractmethod

class VQAModelPort(ABC):

    @abstractmethod
    def answer_question(self, image_bytes: bytes, question: str) -> str:
        """Answer question about the image"""
        pass
