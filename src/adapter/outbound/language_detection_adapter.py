from deep_translator import GoogleTranslator
import langdetect
from application.port.outbound.language_detection_port import LanguageDetectionPort

class LanguageDetectionAdapter(LanguageDetectionPort):

    def detect_language(self, text: str) -> str:
        try:
            detected = langdetect.detect(text)
            print(f"DEBUG [LangDetect]: Text '{text}' detected as '{detected}'")
            return detected
        except Exception as e:
            print(f"WARNING [LangDetect]: Failed to detect language for '{text}': {str(e)}")
            return "unknown"

    def translate_to_english(self, text: str) -> str:
        try:
            return GoogleTranslator(source='ko', target='en').translate(text)
        except Exception as e:
            print(f"Error during translation: {e}")
            return text
