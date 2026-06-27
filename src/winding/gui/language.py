import tomllib
import os
import sys

class LanguageManager:
    def __init__(self, default_lang="english"):
        self.lang_dir = self.get_asset_path(os.path.join("assets", "lang"))
        self.current_lang = default_lang
        self.strings = {}
        self.registered_widgets = []
        
        self.load_language(default_lang)

    def get_asset_path(self, relative_path):
        """Resolves a path relative to the root directory, supporting PyInstaller bundles."""
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            # language.py is in src/winding/gui/, so parent of parent is src/winding/
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    def load_language(self, lang_name):
        self.current_lang = lang_name
        file_path = os.path.join(self.lang_dir, f"{lang_name}.toml")
        
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                self.strings = tomllib.load(f)
        else:
            print(f"Warning: Language file {file_path} not found!")
            self.strings = {}

        self._update_all_widgets()

    def get(self, dotted_key):
        """Retrieves a nested string from the TOML data using dotted notation."""
        parts = dotted_key.split(".")
        val = self.strings
        for part in parts:
            if isinstance(val, dict) and part in val:
                val = val[part]
            else:
                return f"[{dotted_key}]"
        return str(val)

    def register(self, widget, text_key):
        self.registered_widgets.append((widget, text_key))
        self._update_single_widget(widget, text_key)

    def _update_single_widget(self, widget, text_key):
        translated_text = self.get(text_key)
        try:
            widget.configure(text=translated_text)
        except Exception:
            pass

    def _update_all_widgets(self):
        alive_widgets = []
        for widget, key in self.registered_widgets:
            if widget.winfo_exists():
                self._update_single_widget(widget, key)
                alive_widgets.append((widget, key))
        self.registered_widgets = alive_widgets
