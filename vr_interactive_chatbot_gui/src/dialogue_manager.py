import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

class DialogueManager:
    def __init__(self, history_path: str = "data/chat_history.json", max_limit: int = 100, logger: Optional[logging.Logger] = None):
        self.history_path = history_path
        self.max_limit = max_limit
        self.logger = logger or logging.getLogger("VREnterpriseLogger")
        self.session_history: List[Dict[str, Any]] = []

    def record_turn(self, query: str, intent: str, confidence: float, response: str) -> None:
        turn = {
            "timestamp": datetime.now().isoformat(),
            "user_query": query,
            "intent": intent,
            "confidence": confidence,
            "bot_response": response
        }
        self.session_history.append(turn)
        if len(self.session_history) > self.max_limit:
            self.session_history.pop(0)

    def get_summary(self) -> dict:
        return {
            "total_interactions": len(self.session_history),
            "intents_triggered": list(set(item["intent"] for item in self.session_history))
        }