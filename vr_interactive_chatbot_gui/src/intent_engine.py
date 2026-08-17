import json
import re
import random
import logging
from typing import Dict, List, Tuple, Any, Optional

class IntentEngine:
    def __init__(self, intents_path: str = "data/intents.json", confidence_threshold: float = 0.40, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("VREnterpriseLogger")
        self.confidence_threshold = confidence_threshold
        self.intents = self._load_intents(intents_path)

    def _load_intents(self, path: str) -> List[Dict[str, Any]]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("intents", [])
        except Exception:
            return []

    def classify(self, raw_input: str, nlp_data: Dict[str, Any]) -> Tuple[str, float, str]:
        lemmas = nlp_data.get("lemmas", [])

        # Layer 1: Regex
        for intent in self.intents:
            tag = intent["tag"]
            for pattern in intent["patterns"]:
                if re.search(r'\b' + pattern + r'\b', raw_input, re.IGNORECASE):
                    response = random.choice(intent["responses"])
                    return tag, 0.95, response

        # Layer 2: Keyword Scoring
        best_intent = None
        max_score = 0.0

        for intent in self.intents:
            keywords = intent["keywords"]
            if not keywords:
                continue
            matches = sum(1 for lemma in lemmas if lemma in keywords)
            score = matches / len(keywords)
            if score > max_score:
                max_score = score
                best_intent = intent

        if best_intent and max_score >= self.confidence_threshold:
            tag = best_intent["tag"]
            response = random.choice(best_intent["responses"])
            return tag, float(max_score), response

        fallbacks = [
            "I'm sorry, that query is outside my current rule base. Try asking about VR features or architecture.",
            "Could you rephrase that? I am specialized in VR interactive commands and system FAQs."
        ]
        return "fallback", 0.0, random.choice(fallbacks)