from deep_translator import GoogleTranslator
from langdetect import detect

class LanguageHandler:
    def __init__(self, enabled: bool = True, logger=None):
        self.enabled = enabled
        self.logger = logger

    def detect_language(self, text: str) -> str:
        clean = text.strip()
        if not self.enabled or len(clean) < 12:
            return "en"
        # If text is purely basic ASCII words (standard English characters), default to English
        if clean.isascii():
            return "en"
        try:
            return detect(clean)
        except Exception:
            return "en"

    def to_english(self, text: str, source_lang: str = "auto") -> tuple[str, str]:
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
                self.logger.warning(f"Input translation fallback: {e}")
            return text, detected

    def from_english(self, text: str, target_lang: str) -> str:
        if not self.enabled or not target_lang or target_lang in ("en", "auto"):
            return text
        try:
            translated = GoogleTranslator(source="en", target=target_lang).translate(text)
            return translated or text
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Output translation error: {e}")
            return text
