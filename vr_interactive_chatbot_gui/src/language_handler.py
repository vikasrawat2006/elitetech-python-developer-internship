from deep_translator import GoogleTranslator
from langdetect import detect

class LanguageHandler:
    def __init__(self, enabled: bool = True, logger=None):
        self.enabled = enabled
        self.logger = logger

    def detect_language(self, text: str) -> str:
        if not self.enabled or len(text.strip()) < 3:
            return "en"
        try:
            return detect(text)
        except Exception:
            return "en"

    def to_english(self, text: str, source_lang: str = "auto") -> tuple[str, str]:
        """Translates user input to English and returns (english_text, detected_lang)."""
        if not self.enabled or not text.strip():
            return text, "en"

        detected = self.detect_language(text) if source_lang == "auto" else source_lang
        if detected == "en":
            return text, "en"

        try:
            translated = GoogleTranslator(source="auto", target="en").translate(text)
            return translated or text, detected
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Input translation fallback to raw text: {e}")
            return text, detected

    def from_english(self, text: str, target_lang: str) -> str:
        """Translates English response back to the user's language."""
        if not self.enabled or not target_lang or target_lang in ("en", "auto"):
            return text
        try:
            translated = GoogleTranslator(source="en", target=target_lang).translate(text)
            return translated or text
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Output translation error: {e}")
            return text