"""
Dependency injection factory for controllers
"""
from application.service.recommend_service import RecommendService
from application.service.vqa_service import VQAService
from application.service.tts_service import TTSService
from adapter.outbound.google_translate_adapter import GoogleTranslateAdapter
from adapter.outbound.public_data_adapter import PublicDataAdapter
from adapter.outbound.llm_adapter import LLMAdapter
from adapter.outbound.language_detection_adapter import LanguageDetectionAdapter
from adapter.outbound.image_fetch_adapter import ImageFetchAdapter
from adapter.outbound.elevenlabs_tts_adapter import ElevenLabsTTSAdapter
from adapter.outbound.media_adapter import MediaAdapter
from domain.service.yolo_service import YoloService
from domain.service.vilt_service import ViltService

# Singleton instances for domain services and adapters
_yolo_service = None
_vilt_service = None
_tts_adapter = None
_llm_adapter = None
_language_detection_adapter = None

def get_yolo_service() -> YoloService:
    global _yolo_service
    if _yolo_service is None:
        _yolo_service = YoloService("src/models/best.pt")
    return _yolo_service

def get_vilt_service() -> ViltService:
    global _vilt_service
    if _vilt_service is None:
        _vilt_service = ViltService("dandelin/vilt-b32-finetuned-vqa")
    return _vilt_service

def get_tts_adapter() -> ElevenLabsTTSAdapter:
    global _tts_adapter
    if _tts_adapter is None:
        _tts_adapter = ElevenLabsTTSAdapter()
    return _tts_adapter

def get_llm_adapter() -> LLMAdapter:
    global _llm_adapter
    if _llm_adapter is None:
        _llm_adapter = LLMAdapter()
    return _llm_adapter

def get_language_detection_adapter() -> LanguageDetectionAdapter:
    global _language_detection_adapter
    if _language_detection_adapter is None:
        _language_detection_adapter = LanguageDetectionAdapter()
    return _language_detection_adapter

def get_recommend_service() -> RecommendService:
    translation_port = GoogleTranslateAdapter()
    event_port = PublicDataAdapter()
    return RecommendService(translation_port, event_port)

def get_vqa_service() -> VQAService:
    llm_port = get_llm_adapter()
    image_analysis_port = get_yolo_service()
    vqa_model_port = get_vilt_service()
    language_detection_port = get_language_detection_adapter()
    image_fetch_port = ImageFetchAdapter()
    media_port = MediaAdapter()
    translation_port = GoogleTranslateAdapter()
    return VQAService(
        llm_port,
        image_analysis_port,
        vqa_model_port,
        language_detection_port,
        image_fetch_port,
        media_port,
        translation_port
    )

def get_tts_service() -> TTSService:
    tts_port = get_tts_adapter()
    return TTSService(tts_port)
