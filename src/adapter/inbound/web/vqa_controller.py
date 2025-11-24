from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from application.port.inbound.vqa_use_case import VQAUseCase
from application.port.outbound.llm_port import LLMPort
from application.port.outbound.language_detection_port import LanguageDetectionPort
from domain.model.vqa_model import VQARequest, VQAResponse
from domain.util.text_utils import extract_keywords_from_text
from adapter.inbound.web.dependencies import get_vqa_service, get_llm_adapter, get_language_detection_adapter


class VQARequestDTO(BaseModel):
    media_id: Optional[str] = None
    question: str
    child_name: Optional[str] = None


vqa_router = APIRouter()


@vqa_router.post("/", response_class=JSONResponse)
async def handle_vqa(
    request_dto: VQARequestDTO,
    authorization: Optional[str] = Header(None),
    vqa_service: VQAUseCase = Depends(get_vqa_service),
    llm_port: LLMPort = Depends(get_llm_adapter),
    language_detection_port: LanguageDetectionPort = Depends(get_language_detection_adapter)
):
    """
    이미지(media) 없으면 LLM 직접 질의, 있으면 VQA → LLM 설명 생성
    """
    # Extract token from Authorization header
    token = None
    if authorization:
        # Remove "Bearer " prefix if present
        token = authorization.replace("Bearer ", "").strip()
        print(f"DEBUG: Received token from header (length: {len(token)})")
    # Extract keywords from question
    keywords = extract_keywords_from_text(request_dto.question)
    lang = language_detection_port.detect_language(request_dto.question)

    # If no media_id, use simple LLM response
    if not request_dto.media_id:
        print(f"DEBUG: No media_id, using simple LLM")
        print(f"DEBUG: Question language detected: {lang}")

        # Set default child name based on question language
        default_child_name = "아이" if lang == "ko" else "child"
        child_name = request_dto.child_name or default_child_name
        print(f"DEBUG: Using child_name: {child_name}")

        answer = await llm_port.ask_simple(request_dto.question, child_name, lang)
        return JSONResponse(content={
            "answer": answer,
            "keywords": keywords
        })

    # If media_id provided, use VQA service
    try:
        # Note: child_name will be set to default based on language in vqa_service if not provided
        request = VQARequest(
            image_url=request_dto.media_id,
            question=request_dto.question,
            child_name=request_dto.child_name,
            token=token
        )
        response: VQAResponse = await vqa_service.handle_vqa(request)

        # Return simplified response with answer and keywords
        return JSONResponse(content={
            "answer": response.answer,
            "keywords": response.keywords
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VQA 처리 중 오류: {str(e)}")
