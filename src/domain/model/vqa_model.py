from pydantic import BaseModel
from typing import Optional, List

class VQARequest(BaseModel):
    image_url: str
    question: str
    child_name: Optional[str]
    token: Optional[str] = None

class VQAResponse(BaseModel):
    answer: str
    keywords: List[str]
    vqa_direct_answer: Optional[str] = None
    question: Optional[str] = None
    detected_object: Optional[str] = None
