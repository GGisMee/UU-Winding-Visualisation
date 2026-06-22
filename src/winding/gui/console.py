import customtkinter as ctk
import tkinter as tk
from .theme import Theme
from .components import LabeledSlider, MetricRow, TextInfoBox

class ConsolePanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(
            parent, 
            width=380, 
            fg_color=Theme.BG_SURFACE.value, 
            border_width=1, 
            border_color=Theme.BORDER.value
        )
        # Prevent auto-shrinking
        self.pack_propagate(False)
        self.grid_propagate(False)

        self.create_widgets()

    def create_widgets(self):
        # 1. Title Label
        self.lbl_title = ctk.CTkLabel(
            self, 
            text="CONTROL CONSOLE", 
            font=Theme.fonts.TITLE, 
            text_color=Theme.TEXT_ACCENT.value
        )
        self.lbl_title.pack(anchor="w", padx=15, pady=(15, 5))

        # 2. Main Tabs Widget
        self.tabs = ctk.CTkTabview(
            self, 
            fg_color=Theme.BG_SURFACE.value,
            segmented_button_fg_color=Theme.BOX_BG.value,
            segmented_button_selected_color=Theme.TAB_SELECTED.value,
            segmented_button_selected_hover_color=Theme.TAB_SELECTED_HOVER.value,
            segmented_button_unselected_color=Theme.BOX_BG.value,
            segmented_button_unselected_hover_color=Theme.BUTTON_HOVER.value,
            text_color=Theme.TEXT_MAIN.value
        )
        self.tabs.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tabs.add("Settings")
        
        self.settings_frame = ctk.CTkFrame(self.tabs.tab("Settings"), fg_color=Theme.BG_SURFACE.value)
        self.settings_frame.pack(fill="both", expand=True)

    def set_inputs_enabled(self, enabled: bool):
        pass

    def update_from_models(self):
        pass