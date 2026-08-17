import customtkinter as ctk
from src.chatbot_core import ChatbotCore

class ChatbotGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Core Engine Initialization
        self.core = ChatbotCore()
        
        # Window Configuration
        self.title(self.core.chatbot_name)
        self.geometry("950x650")
        self.minsize(800, 500)
        
        ctk.set_appearance_mode(self.core.config.get("theme", "dark"))
        ctk.set_default_color_theme(self.core.config.get("accent_color", "blue"))

        self._build_layout()
        self._insert_welcome_message()

    def _build_layout(self):
        # Configure Grid Weight
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Sidebar Panel ---
        self.sidebar_frame = ctk.CTkFrame(self, width=260, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        # Sidebar Title
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="VR Chatbot Panel", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Telemetry / Status Box
        self.status_title = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Session Telemetry:", 
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.status_title.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w")

        self.telemetry_box = ctk.CTkTextbox(self.sidebar_frame, width=220, height=200, state="disabled")
        self.telemetry_box.grid(row=2, column=0, padx=20, pady=5)
        self._update_telemetry("Status: Online\nReady for user input.")

        # Theme Switcher
        self.theme_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", font=ctk.CTkFont(size=12))
        self.theme_label.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")

        self.theme_menu = ctk.CTkOptionMenu(
            self.sidebar_frame, 
            values=["Dark", "Light", "System"],
            command=self._change_theme
        )
        self.theme_menu.grid(row=6, column=0, padx=20, pady=(5, 20), sticky="ew")
        self.theme_menu.set("Dark")

        # --- Main Chat Area ---
        self.chat_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.chat_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_frame.grid_columnconfigure(0, weight=1)

        # Scrollable Message Log
        self.chat_scrollable = ctk.CTkScrollableFrame(self.chat_frame, fg_color=("#F5F5F5", "#1A1A1A"))
        self.chat_scrollable.grid(row=0, column=0, sticky="nsew", padx=0, pady=(0, 10))
        self.chat_scrollable.grid_columnconfigure(0, weight=1)

        # Input Frame (Entry + Send Button)
        self.input_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.msg_entry = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Type your query here (e.g., 'What can VR do?')...",
            height=45,
            font=ctk.CTkFont(size=14)
        )
        self.msg_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.msg_entry.bind("<Return>", lambda event: self._handle_user_message())

        self.send_btn = ctk.CTkButton(
            self.input_frame, 
            text="Send", 
            width=100, 
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._handle_user_message
        )
        self.send_btn.grid(row=0, column=1, sticky="e")

    def _append_message(self, sender: str, message: str, intent: str = None):
        bubble_frame = ctk.CTkFrame(self.chat_scrollable, fg_color="transparent")
        bubble_frame.grid(sticky="ew", padx=10, pady=6)
        bubble_frame.grid_columnconfigure(0, weight=1)

        is_user = sender == "You"
        align = "e" if is_user else "w"
        bg_color = ("#3B82F6", "#1D4ED8") if is_user else ("#E5E7EB", "#2D2D2D")
        text_color = ("#FFFFFF", "#FFFFFF") if is_user else ("#111827", "#F3F4F6")

        inner_frame = ctk.CTkFrame(bubble_frame, fg_color=bg_color, corner_radius=12)
        inner_frame.pack(anchor=align, padx=5, pady=2)

        # Sender & Badge Header
        header_text = f"{sender}"
        if intent and not is_user:
            header_text += f" | Intent: [{intent.upper()}]"

        header_label = ctk.CTkLabel(
            inner_frame, 
            text=header_text, 
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=text_color
        )
        header_label.pack(anchor="w", padx=12, pady=(6, 2))

        msg_label = ctk.CTkLabel(
            inner_frame, 
            text=message, 
            font=ctk.CTkFont(size=13),
            text_color=text_color,
            wraplength=500,
            justify="left"
        )
        msg_label.pack(anchor="w", padx=12, pady=(0, 8))

        # Auto-scroll to bottom
        self.chat_scrollable._parent_canvas.yview_moveto(1.0)

    def _insert_welcome_message(self):
        welcome_text = (
            "Hello! I am your VR Interactive NLP Chatbot with Rule-Based Intelligence.\n"
            "Feel free to ask about VR features, system architecture, or type 'exit' to quit."
        )
        self._append_message("Bot", welcome_text, intent="greeting")

    def _handle_user_message(self):
        query = self.msg_entry.get().strip()
        if not query:
            return

        self.msg_entry.delete(0, 'end')
        self._append_message("You", query)

        # Process via Chatbot Core
        result = self.core.process_message(query)
        self._append_message("Bot", result["response"], intent=result["intent"])

        # Update Telemetry Display
        summary = self.core.dialogue_manager.get_summary()
        telemetry_text = (
            f"Total Interactions: {summary['total_interactions']}\n"
            f"Last Intent: {result['intent']}\n"
            f"Confidence: {result['confidence']:.2f}\n"
            f"Status: Active Session"
        )
        self._update_telemetry(telemetry_text)

        if result["intent"] == "goodbye":
            self.after(2000, self.destroy)

    def _update_telemetry(self, text: str):
        self.telemetry_box.configure(state="normal")
        self.telemetry_box.delete("1.0", "end")
        self.telemetry_box.insert("1.0", text)
        self.telemetry_box.configure(state="disabled")

    def _change_theme(self, new_theme: str):
        ctk.set_appearance_mode(new_theme)


if __name__ == "__main__":
    app = ChatbotGUI()
    app.mainloop()