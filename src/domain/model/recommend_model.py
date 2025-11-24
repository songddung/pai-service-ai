from pydantic import BaseModel
from typing import List, Optional

class RecommendRequest(BaseModel):
    user_id: int
    profile_id: int
    category: str
    lat: float
    lon: float

class Festival(BaseModel):
    title: str
    address: str
    lat: float
    lon: float
    distance_km: float
    first_image: Optional[str] = None
    tel: Optional[str] = None

class RecommendResponse(BaseModel):
    user_id: int
    profile_id: int
    translated_category: str
    festivals: List[Festival]
