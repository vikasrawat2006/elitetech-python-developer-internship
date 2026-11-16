import json
from typing import Dict, Any
from src.logger_setup import setup_enterprise_logger
from src.preprocessor import NLPPreprocessor
from src.intent_engine import IntentEngine
from src.dialogue_manager import DialogueManager
from src.language_handler import LanguageHandler
from src.document_retriever import VastDataRetriever
from src.api_connector import DualAPIConnector

class ChatbotCore:
    def __init__(self, config_path: str = "config/settings.json"):
        self.config = self._load_config(config_path)
        self.logger = setup_enterprise_logger(level=self.config.get("log_level", "DEBUG"))
        self.chatbot_name = self.config.get("chatbot_name", "VR Interactive Hybrid NLP & AI Chatbot")
        self.threshold = self.config.get("confidence_threshold", 0.40)

        # Core NLP Modules
        self.preprocessor = NLPPreprocessor(logger=self.logger)
        self.intent_engine = IntentEngine(confidence_threshold=self.threshold, logger=self.logger)
        self.dialogue_manager = DialogueManager(max_limit=self.config.get("max_history_limit", 100), logger=self.logger)

        # New Hybrid AI, Multilingual & Vast Data Modules
        self.lang_handler = LanguageHandler(
            enabled=self.config.get("enable_multilanguage", True),
            logger=self.logger
        )
        self.retriever = VastDataRetriever(
            docs_dir=self.config.get("knowledge_docs_dir", "data/knowledge_docs"),
            logger=self.logger
        )
        self.api_connector = DualAPIConnector(config=self.config, logger=self.logger)
        self.chat_memory = []

    def _load_config(self, path: str) -> Dict[str, Any]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {
                "chatbot_name": "VR Interactive Hybrid NLP & AI Chatbot",
                "version": "4.0.0",
                "confidence_threshold": 0.40
            }

    def process_message(self, user_input: str, target_lang: str = "auto") -> Dict[str, Any]:
        cleaned_query = user_input.strip()
        if not cleaned_query:
            return {
                "intent": "empty",
                "confidence": 0.0,
                "response": "Please provide a valid query.",
                "source": "System",
                "language": "en"
            }

        # Step 1: Translate input to English if needed
        eng_query, detected_lang = self.lang_handler.to_english(cleaned_query, source_lang=target_lang)
        reply_lang = detected_lang if target_lang == "auto" else target_lang

        # Step 2: Check Vast Data Knowledge Base (RAG) FIRST if documents are loaded
        doc_context, matched_files = self.retriever.retrieve_context(eng_query)
        doc_keywords = ("document", "pdf", "file", "uploaded", "synopsis", "notes", "page", "book", "data")
        force_doc_qa = any(k in eng_query.lower() for k in doc_keywords) and len(self.retriever.chunks) > 0

        if doc_context or force_doc_qa:
            ai_response, api_provider = self.api_connector.generate_response(
                query=eng_query,
                doc_context=doc_context,
                history=self.chat_memory
            )
            response = ai_response
            intent = "rag_knowledge_qa"
            confidence = 0.98
            source_label = f"{api_provider} + Docs ({', '.join(matched_files) if matched_files else 'Knowledge Base'})"
        else:
            # Step 3: Check fast local NLTK Intent Engine
            nlp_data = self.preprocessor.transform(eng_query)
            intent, confidence, response = self.intent_engine.classify(eng_query, nlp_data)
            source_label = "Local NLTK Intent"

            # Step 4: If local confidence is below threshold, use Dual Free Cloud APIs
            if confidence < self.threshold or intent == "fallback":
                ai_response, api_provider = self.api_connector.generate_response(
                    query=eng_query,
                    doc_context="",
                    history=self.chat_memory
                )
                response = ai_response
                intent = "cloud_ai_fallback"
                confidence = 0.95
                source_label = api_provider

        # Step 5: Translate response back to user's language
        final_response = self.lang_handler.from_english(response, reply_lang)

        # Step 6: Record turn in audit log & short-term memory
        self.dialogue_manager.record_turn(cleaned_query, intent, confidence, final_response)
        self.chat_memory.append({"role": "user", "content": eng_query})
        self.chat_memory.append({"role": "assistant", "content": response})
        if len(self.chat_memory) > 20:
            self.chat_memory = self.chat_memory[-20:]

        return {
            "intent": intent,
            "confidence": confidence,
            "response": final_response,
            "source": source_label,
            "language": reply_lang
        }