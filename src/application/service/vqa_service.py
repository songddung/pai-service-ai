from fastapi import HTTPException
from deep_translator import GoogleTranslator
import langdetect
import httpx

from application.port.inbound.vqa_use_case import VQAUseCase
from domain.model.vqa_model import VQARequest, VQAResponse
from domain.service import yolo_service, vilt_service
from adapter.outbound.llm_adapter import LLMAdapter

def load_vqa_models():
    print("--- VQA Module Loading ---")
    yolo_service.load_yolo_model("src/models/best.pt")
    vilt_service.load_vilt_model("dandelin/vilt-b32-finetuned-vqa")
    print("--- VQA Module Loaded ---")

def translate_to_english(text: str) -> str:
    try:
        return GoogleTranslator(source='ko', target='en').translate(text)
    except Exception as e:
        print(f"Error during translation: {e}")
        return text

def detect_language(text: str) -> str:
    try:
        return langdetect.detect(text)
    except:
        return "unknown"

def add_subject_particle(name: str) -> str:
    last_char = name[-1]
    code = ord(last_char) - 0xAC00
    jongseong = code % 28
    return name if jongseong == 0 else name + "이"

async def fetch_image_from_url(url: str) -> bytes:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"이미지 다운로드 실패: {e}")

class VQAService(VQAUseCase):

    def __init__(self):
        self.llm_adapter = LLMAdapter()

    async def handle_vqa(self, request: VQARequest) -> VQAResponse:
        if not vilt_service.model:
            raise HTTPException(status_code=503, detail="VQA model is not loaded.")

        child_name = request.child_name or "아이"

        image_bytes = await fetch_image_from_url(request.image_url)
        yolo_label = yolo_service.analyze_image(image_bytes)
        lang = detect_language(request.question)
        question_for_vqa = translate_to_english(request.question) if lang == "ko" else request.question
        vqa_answer = vilt_service.answer_question_bytes(image_bytes, question_for_vqa)
        child_with_particle = add_subject_particle(child_name)

        if lang == "ko":
            prompt = (
                f"{child_with_particle}가 사진을 보면서 이렇게 물었어:\n"
                f'"{request.question}"\n\n'
                f"그에 대한 답은 \"{vqa_answer}\"야.\n\n"
                f"이제 부모님인 내가 {child_with_particle}에게 짧고 쉽게, 따뜻하게 설명해줄게.\n"
                f"{child_with_particle} 눈높이에 맞게 2~3문장 이내로 말해줘."
            )
        else:
            prompt = (
                f"{child_name} asked this question while looking at the picture:\n"
                f'"{request.question}"\n\n'
                f"The answer is \"{vqa_answer}\”.\n\n"
                f"Now, as a parent, explain it to {child_name} in a kind, simple way, within 2–3 sentences, easy for a child to understand."
            )

        final_answer = await self.llm_adapter.call_llm(prompt, lang)

        return VQAResponse(
            answer=final_answer,
            vqa_direct_answer=vqa_answer,
            question=request.question,
            detected_object=yolo_label,
        )
