import customtkinter as ctk
import tkinter as tk
from .theme import Theme

class CADCanvas(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(
            parent, 
            fg_color=Theme.BG_SURFACE.value, 
            border_width=1, 
            border_color=Theme.BORDER.value
        )
        
        # Get parent scale factor if set
        self.scale_factor = getattr(parent, "scale_factor", 1.0)

        # Title Label
        self.lbl_title = ctk.CTkLabel(
            self, 
            text="CAD CANVAS", 
            font=Theme.fonts.SUBTITLE, 
            text_color=Theme.TEXT_MAIN.value
        )
        self.lbl_title.pack(anchor="w", padx=15, pady=(15, 5))

        # Canvas drawing container
        mode_idx = 0 if ctk.get_appearance_mode() == "Light" else 1
        self.canvas = tk.Canvas(self, bg=Theme.BLUEPRINT_BG.value[mode_idx], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=15, pady=(5, 5))

        # Bind resize event to redraw canvas dynamically
        self.canvas.bind("<Configure>", lambda e: self.update_geometry())

    def update_geometry(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10 or h < 10:
            return

        mode = ctk.get_appearance_mode()
        idx = 0 if mode == "Light" else 1

        bg_color = Theme.BLUEPRINT_BG.value[idx]
        self.canvas.delete("all")
        self.canvas.configure(bg=bg_color)
        
        # Update frame styling
        self.configure(fg_color=Theme.BG_SURFACE.value, border_color=Theme.BORDER.value)