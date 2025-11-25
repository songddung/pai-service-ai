from fastapi import APIRouter, File, UploadFile, Form, Depends
from fastapi.responses import StreamingResponse, Response
from typing import List

from application.port.inbound.tts_use_case import TTSUseCase
from domain.model.tts_model import GuideScriptsResponse, VoiceProfileResponse, VoiceProfileItem, TTSRequest, StreamTTSRequest, DeleteVoiceProfileRequest
from adapter.inbound.web.dependencies import get_tts_service

tts_router = APIRouter()

@tts_router.get("/voice-profiles/scripts", response_model=GuideScriptsResponse)
def get_guide_scripts(tts_service: TTSUseCase = Depends(get_tts_service)):
    return tts_service.get_guide_scripts()

@tts_router.get("/voice-profiles", response_model=List[VoiceProfileItem])
async def get_cloned_voice_profiles(tts_service: TTSUseCase = Depends(get_tts_service)):
    return await tts_service.get_cloned_voice_profiles()

@tts_router.post("/voice-profiles", response_model=VoiceProfileResponse, status_code=201)
async def create_voice_profile(
    account_id: str = Form(...),
    profile_name: str = Form(...),
    audio_file: UploadFile = File(...),
    tts_service: TTSUseCase = Depends(get_tts_service)
):
    return await tts_service.create_voice_profile(account_id, profile_name, audio_file)

@tts_router.delete("/voice-profiles/{profile_id}", status_code=200)
async def delete_voice_profile(profile_id: str, request: DeleteVoiceProfileRequest, tts_service: TTSUseCase = Depends(get_tts_service)):
    return await tts_service.delete_voice_profile(profile_id, request)

@tts_router.post("/generate")
async def text_to_speech(request: TTSRequest, tts_service: TTSUseCase = Depends(get_tts_service)):
    audio_bytes = await tts_service.text_to_speech(request)
    return Response(content=audio_bytes, media_type="audio/mpeg")

@tts_router.post("/generate/stream")
async def stream_text_to_speech(request: StreamTTSRequest, tts_service: TTSUseCase = Depends(get_tts_service)):
    return StreamingResponse(tts_service.stream_text_to_speech(request), media_type="text/event-stream")
