from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

# 서비스 계층
from application.service.vqa_service import VQAService, detect_language
from application.port.inbound.vqa_use_case import VQAUseCase

# 도메인 모델
from domain.model.vqa_model import VQARequest, VQAResponse

# 어댑터 계층
from adapter.outbound.llm_adapter import LLMAdapter

# 유틸: 키워드 추출
import re
from collections import Counter


def extract_keywords_from_text(text: str) -> list:
    words = re.findall(r'[가-힣a-zA-Z]+', text)
    stopwords = {
        "해", "말", "되", "이", "그", "이런", "너", "저", "좀", "정도", "등", "이제", "너희", "여기", "저기",
        "이거", "그거", "저거", "봐", "들", "주세요", "요", "습니다", "입니다", "있다", "없다", "같다", "보다",
        "오", "가", "올", "갈", "할", "주", "줘", "수", "때", "거", "것", "하는", "한", "네", "응", "아니",
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are",
        "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should",
        "this", "that", "these", "those", "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us",
        "them", "my", "your", "his", "her", "its", "our", "their", "mine", "yours", "hers", "ours", "theirs"
    }
    keywords = [word for word in words if len(word) > 1 and word.lower() not in stopwords]
    freq = Counter(keywords)
    return [item[0] for item in freq.most_common(5)]


vqa_router = APIRouter()


def get_vqa_service() -> VQAUseCase:
    return VQAService()

def get_llm_adapter() -> LLMAdapter:
    return LLMAdapter()

@vqa_router.post("/", response_class=JSONResponse)
async def handle_vqa(
    media_id: Optional[str] = Form(None),
    question: str = Form(...),
    child_name: Optional[str] = Form(None),
    vqa_service: VQAUseCase = Depends(get_vqa_service),
    llm_adapter: LLMAdapter = Depends(get_llm_adapter)
):
    """
    이미지(media) 없으면 LLM 직접 질의, 있으면 VQA → LLM 설명 생성
    """
    # 1. 키워드 추출 (항상 수행)
    keywords = extract_keywords_from_text(question)

    # 2. 언어 감지 (간단변수)
    lang = detect_language(question)

    # 3. 분기: image/media 없는 경우 → LLM 단순 답변
    if not media_id:
        # `ask_simple`은 LLMAdapter에 구현되어 있어야 함
        answer = await llm_adapter.ask_simple(question,child_name, lang)
        return JSONResponse(content={
            "answer": answer,
            "keywords": keywords,
            "question": question,
            "detected_object": "No image provided"
        })

    # 4. 이미지(media) 있는 경우 → VQAService 처리
    try:
        request = VQARequest(
            image_url=media_id,
            question=question,
            child_name=child_name
        )
        response: VQAResponse = await vqa_service.handle_vqa(request)
        return JSONResponse(content=response.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VQA 처리 중 오류: {str(e)}")
