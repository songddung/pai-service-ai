from abc import ABC, abstractmethod

class LLMPort(ABC):

    @abstractmethod
    async def call_llm(self, prompt: str, lang: str) -> str:
        pass
