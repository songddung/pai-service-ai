from application.port.inbound.recommend_use_case import RecommendUseCase
from domain.model.recommend_model import RecommendRequest, RecommendResponse
from adapter.outbound.google_translate_adapter import GoogleTranslateAdapter
from adapter.outbound.public_data_adapter import PublicDataAdapter

class RecommendService(RecommendUseCase):

    def __init__(self):
        self.translation_adapter = GoogleTranslateAdapter()
        self.event_adapter = PublicDataAdapter()

    def recommend_event(self, req: RecommendRequest) -> RecommendResponse:
        translated_category = self.translation_adapter.translate_text(req.category)
        festivals = self.event_adapter.get_festivals(translated_category, req.lat, req.lon)

        return RecommendResponse(
            user_id=req.user_id,
            profile_id=req.profile_id,
            translated_category=translated_category,
            festivals=festivals,
        )
