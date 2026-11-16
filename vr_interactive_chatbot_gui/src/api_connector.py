import os
import wikipediaapi
from google import genai
from google.genai import types
from groq import Groq

class DualAPIConnector:
    def __init__(self, config: dict, logger=None):
        self.logger = logger
        self.last_error = "None"
        self.gemini_key = (os.getenv("GEMINI_API_KEY") or config.get("gemini_api_key", "")).strip().strip('"').strip("'")
        self.gemini_model = config.get("gemini_model", "gemini-2.5-flash")
        self.groq_key = (os.getenv("GROQ_API_KEY") or config.get("groq_api_key", "")).strip().strip('"').strip("'")
        self.groq_model = config.get("groq_model", "llama-3.3-70b-versatile")

        self.gemini_client = None
        if self.gemini_key and not self.gemini_key.startswith("YOUR_"):
            try:
                self.gemini_client = genai.Client(api_key=self.gemini_key)
            except Exception as e:
                self.last_error = f"Gemini Init Error: {e}"

        self.groq_client = None
        if self.groq_key and not self.groq_key.startswith("YOUR_"):
            try:
                self.groq_client = Groq(api_key=self.groq_key)
            except Exception as e:
                self.last_error = f"Groq Init Error: {e}"

        self.wiki = wikipediaapi.Wikipedia(user_agent="VR_Hybrid_NLP_Chatbot/4.0", language="en")

    def generate_response(self, query: str, doc_context: str = "", history: list = None) -> tuple[str, str]:
        """Returns (response_text, provider_used)."""
        errors = []
        system_instruction = (
            "You are VR Interactive AI Assistant, an intelligent, accurate, and helpful assistant. "
            "Answer clearly and concisely. If document context is provided below, prioritize facts from it."
        )
        if doc_context:
            system_instruction += f"\n\n--- LOCAL KNOWLEDGE BASE CONTEXT ---\n{doc_context}"

        # 1. Try Primary: Google Gemini API
        if self.gemini_client:
            for model_name in (self.gemini_model, "gemini-2.5-flash-lite", "gemini-2.0-flash"):
                try:
                    prompt_text = query
                    if history:
                        recent = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in history[-6:])
                        prompt_text = f"Conversation History:\n{recent}\n\nUser Question: {query}"

                    res = self.gemini_client.models.generate_content(
                        model=model_name,
                        contents=prompt_text,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.5,
                        ),
                    )
                    if res and res.text:
                        self.last_error = "None"
                        return res.text.strip(), f"Gemini ({model_name})"
                except Exception as e:
                    errors.append(f"Gemini [{model_name}]: {e}")

        # 2. Try Secondary: GroqCloud API
        if self.groq_client:
            for g_model in (self.groq_model, "llama-3.1-8b-instant"):
                try:
                    messages = [{"role": "system", "content": system_instruction}]
                    if history:
                        messages.extend(history[-6:])
                    messages.append({"role": "user", "content": query})

                    completion = self.groq_client.chat.completions.create(
                        model=g_model,
                        messages=messages,
                        temperature=0.5,
                    )
                    reply = completion.choices[0].message.content
                    if reply:
                        self.last_error = "None"
                        return reply.strip(), f"Groq ({g_model})"
                except Exception as e:
                    errors.append(f"Groq [{g_model}]: {e}")

        # 3. Record exact error and fall back to Wikipedia
        self.last_error = " | ".join(errors) if errors else "No valid API keys configured."
        if self.logger:
            self.logger.warning(f"Cloud APIs failed: {self.last_error}")

        return self._query_wikipedia(query), f"Wikipedia Fallback ({self.last_error[:90]})"

    def _query_wikipedia(self, query: str) -> str:
        clean_topic = query.lower()
        for prefix in ("what is", "who is", "tell me about", "define", "explain"):
            clean_topic = clean_topic.replace(prefix, "")
        clean_topic = clean_topic.replace("?", "").strip()

        page = self.wiki.page(clean_topic)
        if page.exists():
            return f"{page.summary[:600]}..."
        return "I couldn't match a local intent, and both cloud APIs are currently unavailable or unconfigured."
