from abc import ABC, abstractmethod
from typing import List, AsyncGenerator
from fastapi import UploadFile
from domain.model.tts_model import GuideScriptsResponse, VoiceProfileResponse, VoiceProfileItem, TTSRequest, StreamTTSRequest, DeleteVoiceProfileRequest

class TTSUseCase(ABC):

    @abstractmethod
    def get_guide_scripts(self) -> GuideScriptsResponse:
        pass

    @abstractmethod
    async def get_cloned_voice_profiles(self) -> List[VoiceProfileItem]:
        pass

    @abstractmethod
    async def create_voice_profile(self, account_id: str, profile_name: str, audio_file: UploadFile) -> VoiceProfileResponse:
        pass

    @abstractmethod
    async def delete_voice_profile(self, profile_id: str, request: DeleteVoiceProfileRequest) -> dict:
        pass

    @abstractmethod
    async def text_to_speech(self, request: TTSRequest) -> bytes:
        pass

    @abstractmethod
    def stream_text_to_speech(self, request: StreamTTSRequest) -> AsyncGenerator[str, None]:
        pass
