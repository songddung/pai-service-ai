from fastapi import UploadFile
import json, base64
from typing import List, AsyncGenerator

from application.port.inbound.tts_use_case import TTSUseCase
from application.port.outbound.tts_port import TTSPort
from domain.model.tts_model import GuideScriptsResponse, VoiceProfileResponse, VoiceProfileItem, TTSRequest, StreamTTSRequest, DeleteVoiceProfileRequest

GUIDE_SCRIPTS = {
    "ko": [
        "음성 복제 기술은 다양한 분야에서 활용될 수 있는 잠재력을 가지고 있습니다.",
        "정확한 발음으로 천천히, 그리고 꾸준한 톤으로 말씀해주세요.",
        "이 문장은 시스템이 당신의 목소리 특징을 학습하는 데 사용됩니다."
    ],
    "en": [
        "Voice cloning technology has the potential to be used in various fields.",
        "Please speak slowly with clear pronunciation and a steady tone.",
        "This sentence will be used by the system to learn the characteristics of your voice."
    ]
}

class TTSService(TTSUseCase):

    def __init__(self, tts_port: TTSPort):
        self.tts_port = tts_port

    def get_guide_scripts(self) -> GuideScriptsResponse:
        return GUIDE_SCRIPTS

    async def get_cloned_voice_profiles(self) -> List[VoiceProfileItem]:
        return await self.tts_port.get_cloned_voice_profiles()

    async def create_voice_profile(self, account_id: str, profile_name: str, audio_file: UploadFile) -> VoiceProfileResponse:
        try:
            file_content = await audio_file.read()
        except Exception as e:
            raise Exception(f"Read audio failed: {str(e)}")

        result = await self.tts_port.create_voice_profile(profile_name, file_content)
        return {
            "profile_id": result["profile_id"],
            "account_id": account_id,
            "profile_name": result["profile_name"],
            "message": "Voice profile created successfully."
        }

    async def delete_voice_profile(self, profile_id: str, request: DeleteVoiceProfileRequest) -> dict:
        await self.tts_port.delete_voice_profile(profile_id)
        return {"message": f"Voice profile '{profile_id}' deleted successfully."}

    async def text_to_speech(self, request: TTSRequest) -> bytes:
        return await self.tts_port.text_to_speech(request.text, request.profile_id)

    async def stream_text_to_speech(self, request: StreamTTSRequest) -> AsyncGenerator[str, None]:
        async def generate_audio_stream() -> AsyncGenerator[str, None]:
            try:
                async for chunk in self.tts_port.stream_text_to_speech(request.text, request.profile_id):
                    audio_b64 = base64.b64encode(chunk).decode()
                    yield f"data: {json.dumps({'audio': audio_b64})}\n\n"
                yield "data: {\"done\": true}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        return generate_audio_stream()
