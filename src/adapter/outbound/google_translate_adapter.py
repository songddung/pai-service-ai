import os
import requests
from application.port.outbound.translation_port import TranslationPort

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

class GoogleTranslateAdapter(TranslationPort):

    def translate_text(self, text: str, source="en", target="ko") -> str:
        if not text:
            return ""

        print(f"DEBUG [GoogleTranslate]: Translating '{text}' from {source} to {target}")

        url = "https://translation.googleapis.com/language/translate/v2"
        params = {
            "q": text,
            "source": source,
            "target": target,
            "format": "text",
            "key": GOOGLE_API_KEY,
        }

        print(f"DEBUG [GoogleTranslate]: API Key present: {bool(GOOGLE_API_KEY)}")

        res = requests.get(url, params=params)

        print(f"DEBUG [GoogleTranslate]: Response status: {res.status_code}")

        if res.status_code != 200:
            print(f"ERROR [GoogleTranslate]: API error: {res.text}")
            raise Exception(f"Google Translate API error: {res.status_code} - {res.text}")

        result = res.json()["data"]["translations"][0]["translatedText"]
        print(f"DEBUG [GoogleTranslate]: Translation result: '{result}'")

        return result
