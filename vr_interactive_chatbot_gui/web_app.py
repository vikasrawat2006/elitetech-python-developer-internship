import os
import nltk
import streamlit as st
from src.chatbot_core import ChatbotCore

st.set_page_config(page_title="VR AI & NLP Chatbot", page_icon="🤖", layout="centered")

# Bridge Streamlit Cloud Secrets into environment variables (ignored locally if no secrets.toml exists)
try:
    for key in ("GEMINI_API_KEY", "GROQ_API_KEY"):
        if key in st.secrets and not os.getenv(key):
            os.environ[key] = st.secrets[key]
except Exception:
    pass

@st.cache_resource
def load_bot():
    for pkg in ("punkt", "punkt_tab", "wordnet"):
        nltk.download(pkg, quiet=True)
    return ChatbotCore("config/settings.json")

bot = load_bot()

# --- Sidebar Controls ---
with st.sidebar:
    st.title("⚙️ Chatbot Controls")
    st.caption("Hybrid NLTK + Gemini/Groq Failover + Vast Data RAG")

    lang_options = {
        "Auto-Detect Language": "auto",
        "English": "en",
        "Hindi (हिन्दी)": "hi",
        "Spanish (Español)": "es",
        "French (Français)": "fr",
        "German (Deutsch)": "de",
        "Arabic (العربية)": "ar",
        "Japanese (日本語)": "ja"
    }
    selected_label = st.selectbox("🌐 Response Language", list(lang_options.keys()))
    selected_lang = lang_options[selected_label]

    st.divider()
    st.subheader("📚 Vast Data Knowledge Base")
    uploaded_files = st.file_uploader(
        "Upload PDF, TXT, or MD files to ask questions from them:",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True
    )
    if uploaded_files:
        if "indexed_files" not in st.session_state:
            st.session_state.indexed_files = set()
        for up_file in uploaded_files:
            if up_file.name not in st.session_state.indexed_files:
                if bot.retriever.add_document_from_bytes(up_file, up_file.name):
                    st.session_state.indexed_files.add(up_file.name)
                    st.success(f"Indexed: {up_file.name}")

    st.info(f"Indexed Knowledge Chunks: **{len(bot.retriever.chunks)}**")

    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        bot.chat_memory = []
        st.rerun()

# --- Main Chat Window ---
st.title("🤖 VR Interactive Hybrid AI Chatbot")
st.caption("Ask anything in any language, query uploaded PDFs, or test local NLP intents.")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I am upgraded with **Multi-Language Support**, **Vast Document Q&A**, and **Dual Cloud AI (Gemini + Groq)** failover. How can I help you?",
            "meta": "System Ready"
        }
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("meta"):
            st.caption(f"⚡ {msg['meta']}")

if prompt := st.chat_input("Type your message in English, Hindi, or any language..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = bot.process_message(prompt, target_lang=selected_lang)
            reply = result["response"]
            meta_info = f"Source: {result['source']} | Intent: {result['intent']} | Lang: {result['language']}"
            st.markdown(reply)
            st.caption(f"⚡ {meta_info}")

    st.session_state.messages.append({"role": "assistant", "content": reply, "meta": meta_info})