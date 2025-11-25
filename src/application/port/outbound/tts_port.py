from abc import ABC, abstractmethod
from typing import List, AsyncGenerator
from fastapi import UploadFile

class TTSPort(ABC):

    @abstractmethod
    async def get_cloned_voice_profiles(self) -> List[dict]:
        """Get list of cloned voice profiles"""
        pass

    @abstractmethod
    async def create_voice_profile(self, profile_name: str, audio_file_content: bytes) -> dict:
        """Create a new voice profile"""
        pass

    @abstractmethod
    async def delete_voice_profile(self, profile_id: str) -> None:
        """Delete a voice profile"""
        pass

    @abstractmethod
    async def text_to_speech(self, text: str, profile_id: str) -> bytes:
        """Convert text to speech using specified voice profile"""
        pass

    @abstractmethod
    async def stream_text_to_speech(self, text: str, profile_id: str) -> AsyncGenerator[bytes, None]:
        """Stream text to speech using specified voice profile"""
        pass
