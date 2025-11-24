from pydantic import BaseModel
from typing import List

class GuideScriptsResponse(BaseModel):
    ko: List[str]
    en: List[str]

class TTSRequest(BaseModel):
    account_id: str
    profile_id: str
    text: str

class StreamTTSRequest(BaseModel):
    account_id: str
    profile_id: str
    text: str

class VoiceProfileInfo(BaseModel):
    profile_id: str
    profile_name: str

class VoiceProfileResponse(VoiceProfileInfo):
    account_id: str
    message: str

class DeleteVoiceProfileRequest(BaseModel):
    account_id: str

class VoiceProfileItem(BaseModel):
    profile_id: str
    profile_name: str
