from pydantic import BaseModel
from typing import Optional

class VQARequest(BaseModel):
    image_url: str
    question: str
    child_name: Optional[str]

class VQAResponse(BaseModel):
    answer: str
    vqa_direct_answer: str
    question: str
    detected_object: str
