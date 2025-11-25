from abc import ABC, abstractmethod

class LanguageDetectionPort(ABC):

    @abstractmethod
    def detect_language(self, text: str) -> str:
        """Detect the language of given text"""
        pass

    @abstractmethod
    def translate_to_english(self, text: str) -> str:
        """Translate text to English"""
        pass
