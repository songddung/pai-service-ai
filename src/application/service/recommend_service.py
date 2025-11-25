from application.port.inbound.recommend_use_case import RecommendUseCase
from application.port.outbound.translation_port import TranslationPort
from application.port.outbound.event_port import EventPort
from domain.model.recommend_model import RecommendRequest, RecommendResponse

class RecommendService(RecommendUseCase):

    def __init__(self, translation_port: TranslationPort, event_port: EventPort):
        self.translation_port = translation_port
        self.event_port = event_port

    def recommend_event(self, req: RecommendRequest) -> RecommendResponse:
        translated_category = self.translation_port.translate_text(req.category)
        festivals = self.event_port.get_festivals(translated_category, req.lat, req.lon)

        return RecommendResponse(
            user_id=req.user_id,
            profile_id=req.profile_id,
            translated_category=translated_category,
            festivals=festivals,
        )
