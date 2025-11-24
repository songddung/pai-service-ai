from fastapi import HTTPException, UploadFile
from elevenlabs.client import ElevenLabs
from elevenlabs.core import ApiError
from dotenv import load_dotenv
import os, json, base64, asyncio
from typing import List, AsyncGenerator

from application.port.inbound.tts_use_case import TTSUseCase
from domain.model.tts_model import GuideScriptsResponse, VoiceProfileResponse, VoiceProfileItem, TTSRequest, StreamTTSRequest, DeleteVoiceProfileRequest

# --- Global ---
elevenlabs_client: ElevenLabs = None
TTS_OUTPUT_DIR = "data/tts_results"

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

def load_tts_model():
    global elevenlabs_client
    print("--- TTS Module Loading (ElevenLabs) ---")
    load_dotenv()
    os.makedirs(TTS_OUTPUT_DIR, exist_ok=True)
    print(f"TTS audio files will be saved in: {os.path.abspath(TTS_OUTPUT_DIR)}")
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("FATAL: ELEVENLABS_API_KEY environment variable not found.")
        elevenlabs_client = None
    else:
        try:
            elevenlabs_client = ElevenLabs(api_key=api_key)
            print("ElevenLabs client initialized successfully.")
        except Exception as e:
            print(f"FATAL: Could not initialize ElevenLabs client: {e}")
            elevenlabs_client = None
    print("--- TTS Module Loaded ---")

class TTSService(TTSUseCase):

    def get_guide_scripts(self) -> GuideScriptsResponse:
        return GUIDE_SCRIPTS

    async def get_cloned_voice_profiles(self) -> List[VoiceProfileItem]:
        if elevenlabs_client is None:
            raise HTTPException(status_code=503, detail="TTS service unavailable")

        try:
            result_data = elevenlabs_client.voices.search(category="cloned")
            result = [
                {"profile_id": v.voice_id, "profile_name": v.name}
                for v in result_data.voices
            ]
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    async def create_voice_profile(self, account_id: str, profile_name: str, audio_file: UploadFile) -> VoiceProfileResponse:
        if elevenlabs_client is None:
            raise HTTPException(status_code=503, detail="TTS service unavailable")
        try:
            file_content = await audio_file.read()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Read audio failed: {str(e)}")
        try:
            voice = elevenlabs_client.voices.ivc.create(
                name=profile_name,
                files=[file_content]
            )
            profile_id = voice.voice_id
            return {
                "profile_id": profile_id,
                "account_id": account_id,
                "profile_name": profile_name,
                "message": "Voice profile created successfully."
            }
        except ApiError as e:
            error_message = e.body.get('detail', {}).get('message', 'Create voice failed')
            raise HTTPException(status_code=e.status_code, detail=f"ElevenLabs API Error: {error_message}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    async def delete_voice_profile(self, profile_id: str, request: DeleteVoiceProfileRequest) -> dict:
        if elevenlabs_client is None:
            raise HTTPException(status_code=503, detail="TTS service unavailable")
        try:
            elevenlabs_client.voices.delete(voice_id=profile_id)
            return {"message": f"Voice profile '{profile_id}' deleted successfully."}
        except ApiError as e:
            err = e.body.get('detail', {}).get('message', 'Delete failed')
            raise HTTPException(status_code=e.status_code, detail=f"ElevenLabs API Error: {err}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    async def text_to_speech(self, request: TTSRequest) -> bytes:
        if elevenlabs_client is None:
            raise HTTPException(status_code=503, detail="TTS service unavailable")
        try:
            audio_generator = elevenlabs_client.text_to_speech.convert(
                text=request.text,
                voice_id=request.profile_id,
                model_id="eleven_multilingual_v2"
            )
            return b"".join(audio_generator)
        except ApiError as e:
            msg = e.body.get('detail', {}).get('message', 'Generate failed')
            raise HTTPException(status_code=e.status_code, detail=f"ElevenLabs API Error: {msg}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")

    async def stream_text_to_speech(self, request: StreamTTSRequest) -> AsyncGenerator[str, None]:
        if elevenlabs_client is None:
            raise HTTPException(status_code=503, detail="TTS service unavailable")

        async def generate_audio_stream() -> AsyncGenerator[str, None]:
            try:
                stream = elevenlabs_client.text_to_speech.stream(
                    text=request.text,
                    voice_id=request.profile_id,
                    model_id="eleven_multilingual_v2"
                )
                for chunk in stream:
                    if chunk:
                        audio_b64 = base64.b64encode(chunk).decode()
                        yield f"data: {json.dumps({'audio': audio_b64})}\n\n"
                        await asyncio.sleep(0.01)
                yield "data: {\"done\": true}\n\n"
            except ApiError as e:
                msg = e.body.get('detail', {}).get('message', 'Streaming failed')
                yield f"data: {json.dumps({'error': 'ElevenLabs API Error: ' + msg})}\\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\\n\n"
        return generate_audio_stream()
