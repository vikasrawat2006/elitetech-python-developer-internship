#!/usr/bin/env python3
"""
Project Title: AI Chatbot with NLP (Internship 8-Week Task)
Chatbot Name: VR Interactive NLP Chatbot with Rule-Based Intelligence
Description: Launches the structured GUI interface for the chatbot.
"""

from ui.app_gui import ChatbotGUI

if __name__ == "__main__":
    app = ChatbotGUI()
    app.mainloop()