import os
import requests
from application.port.outbound.translation_port import TranslationPort

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

class GoogleTranslateAdapter(TranslationPort):

    def translate_text(self, text: str, source="en", target="ko") -> str:
        if not text:
            return ""
        url = "https://translation.googleapis.com/language/translate/v2"
        params = {
            "q": text,
            "source": source,
            "target": target,
            "format": "text",
            "key": GOOGLE_API_KEY,
        }
        res = requests.get(url, params=params)
        return res.json()["data"]["translations"][0]["translatedText"]
