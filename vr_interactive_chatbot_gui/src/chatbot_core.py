import json
from typing import Dict, Any
from src.logger_setup import setup_enterprise_logger
from src.preprocessor import NLPPreprocessor
from src.intent_engine import IntentEngine
from src.dialogue_manager import DialogueManager

class ChatbotCore:
    def __init__(self, config_path: str = "config/settings.json"):
        self.config = self._load_config(config_path)
        self.logger = setup_enterprise_logger(level=self.config.get("log_level", "DEBUG"))
        self.chatbot_name = self.config.get("chatbot_name", "VR Interactive NLP Chatbot with Rule-Based Intelligence")
        
        self.preprocessor = NLPPreprocessor(logger=self.logger)
        self.intent_engine = IntentEngine(confidence_threshold=self.config.get("confidence_threshold", 0.40), logger=self.logger)
        self.dialogue_manager = DialogueManager(max_limit=self.config.get("max_history_limit", 100), logger=self.logger)

    def _load_config(self, path: str) -> Dict[str, Any]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {
                "chatbot_name": "VR Interactive NLP Chatbot with Rule-Based Intelligence",
                "version": "3.5.0",
                "confidence_threshold": 0.40
            }

    def process_message(self, user_input: str) -> Dict[str, Any]:
        cleaned_query = user_input.strip()
        if not cleaned_query:
            return {"intent": "empty", "confidence": 0.0, "response": "Please provide a valid query."}

        nlp_data = self.preprocessor.transform(cleaned_query)
        intent, confidence, response = self.intent_engine.classify(cleaned_query, nlp_data)
        self.dialogue_manager.record_turn(cleaned_query, intent, confidence, response)

        return {
            "intent": intent,
            "confidence": confidence,
            "response": response
        }