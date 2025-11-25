import os
import json
import base64
import asyncio
from typing import List, AsyncGenerator
from elevenlabs.client import ElevenLabs
from elevenlabs.core import ApiError
from fastapi import HTTPException
from dotenv import load_dotenv

from application.port.outbound.tts_port import TTSPort

class ElevenLabsTTSAdapter(TTSPort):

    def __init__(self):
        load_dotenv()
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable not found.")
        self.client = ElevenLabs(api_key=api_key)

    async def get_cloned_voice_profiles(self) -> List[dict]:
        try:
            result_data = self.client.voices.search(category="cloned")
            return [
                {"profile_id": v.voice_id, "profile_name": v.name}
                for v in result_data.voices
            ]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    async def create_voice_profile(self, profile_name: str, audio_file_content: bytes) -> dict:
        try:
            voice = self.client.voices.ivc.create(
                name=profile_name,
                files=[audio_file_content]
            )
            return {
                "profile_id": voice.voice_id,
                "profile_name": profile_name
            }
        except ApiError as e:
            error_message = e.body.get('detail', {}).get('message', 'Create voice failed')
            raise HTTPException(status_code=e.status_code, detail=f"ElevenLabs API Error: {error_message}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    async def delete_voice_profile(self, profile_id: str) -> None:
        try:
            self.client.voices.delete(voice_id=profile_id)
        except ApiError as e:
            err = e.body.get('detail', {}).get('message', 'Delete failed')
            raise HTTPException(status_code=e.status_code, detail=f"ElevenLabs API Error: {err}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    async def text_to_speech(self, text: str, profile_id: str) -> bytes:
        try:
            audio_generator = self.client.text_to_speech.convert(
                text=text,
                voice_id=profile_id,
                model_id="eleven_multilingual_v2"
            )
            return b"".join(audio_generator)
        except ApiError as e:
            msg = e.body.get('detail', {}).get('message', 'Generate failed')
            raise HTTPException(status_code=e.status_code, detail=f"ElevenLabs API Error: {msg}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")

    async def stream_text_to_speech(self, text: str, profile_id: str) -> AsyncGenerator[bytes, None]:
        try:
            stream = self.client.text_to_speech.stream(
                text=text,
                voice_id=profile_id,
                model_id="eleven_multilingual_v2"
            )
            for chunk in stream:
                if chunk:
                    yield chunk
                    await asyncio.sleep(0.01)
        except ApiError as e:
            msg = e.body.get('detail', {}).get('message', 'Streaming failed')
            raise HTTPException(status_code=500, detail=f"ElevenLabs API Error: {msg}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
