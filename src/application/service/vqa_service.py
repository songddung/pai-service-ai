from fastapi import HTTPException

from application.port.inbound.vqa_use_case import VQAUseCase
from application.port.outbound.llm_port import LLMPort
from application.port.outbound.image_analysis_port import ImageAnalysisPort
from application.port.outbound.vqa_model_port import VQAModelPort
from application.port.outbound.language_detection_port import LanguageDetectionPort
from application.port.outbound.image_fetch_port import ImageFetchPort
from application.port.outbound.media_port import MediaPort
from application.port.outbound.translation_port import TranslationPort
from domain.model.vqa_model import VQARequest, VQAResponse
from domain.util.korean_utils import add_subject_particle
from domain.util.text_utils import extract_keywords_from_text

class VQAService(VQAUseCase):

    def __init__(
        self,
        llm_port: LLMPort,
        image_analysis_port: ImageAnalysisPort,
        vqa_model_port: VQAModelPort,
        language_detection_port: LanguageDetectionPort,
        image_fetch_port: ImageFetchPort,
        media_port: MediaPort,
        translation_port: TranslationPort
    ):
        self.llm_port = llm_port
        self.image_analysis_port = image_analysis_port
        self.vqa_model_port = vqa_model_port
        self.language_detection_port = language_detection_port
        self.image_fetch_port = image_fetch_port
        self.media_port = media_port
        self.translation_port = translation_port

    async def handle_vqa(self, request: VQARequest) -> VQAResponse:
        # Detect language from question only
        lang = self.language_detection_port.detect_language(request.question)
        print(f"DEBUG: Question language detected: {lang}")

        # Set default child name based on question language
        default_child_name = "아이" if lang == "ko" else "child"
        child_name = request.child_name or default_child_name
        print(f"DEBUG: Using child_name: {child_name}")

        keywords = extract_keywords_from_text(request.question)

        try:
            # Get media info from media API using token from request
            media_info = await self.media_port.get_media_info(request.image_url, request.token)
            cdn_url = media_info.cdnUrl

            # Download image from CDN URL
            image_bytes = await self.image_fetch_port.fetch_image_from_url(cdn_url)
            yolo_label = self.image_analysis_port.analyze_image(image_bytes)
            question_for_vqa = self.language_detection_port.translate_to_english(request.question) if lang == "ko" else request.question
            vqa_answer = self.vqa_model_port.answer_question(image_bytes, question_for_vqa)
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
                    f"The answer is \"{vqa_answer}\".\n\n"
                    f"Now, as a parent, explain it to {child_name} in a kind, simple way, within 2–3 sentences, easy for a child to understand."
                )

            final_answer = await self.llm_port.call_llm(prompt, lang)

            return VQAResponse(
                answer=final_answer,
                keywords=keywords,
                vqa_direct_answer=vqa_answer,
                question=request.question,
                detected_object=yolo_label,
            )

        except Exception as e:
            # Fallback to simple LLM if image processing fails
            print(f"WARNING: VQA processing failed, falling back to simple LLM: {str(e)}")

            # Use simple LLM response
            answer = await self.llm_port.ask_simple(request.question, child_name, lang)

            return VQAResponse(
                answer=answer,
                keywords=keywords,
                vqa_direct_answer=None,
                question=request.question,
                detected_object=None,
            )
