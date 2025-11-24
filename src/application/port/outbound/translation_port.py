from abc import ABC, abstractmethod

class TranslationPort(ABC):

    @abstractmethod
    def translate_text(self, text: str, source="en", target="ko") -> str:
        pass
