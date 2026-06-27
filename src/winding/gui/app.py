import os
import customtkinter as ctk
import numpy as np
import tkinter as tk
from PIL import Image
from .console import ConsolePanel
from .canvas import CADCanvas
from .analytics import AnalyticsPanel
from .theme import Theme
from ..models.simulation import Geometry, Winding,Magnet, OperatingState, Generator, SimulateGenerator, create_steps
from ..config import WINDOW_SCALING, NB_PERIODS
from .components import ToolTip
from .language import LanguageManager



class UnifiedSimulatorApp(ctk.CTk):
    def __init__(self):
        super().__init__(className="main")

        # --- SCALING & LOOK SETUP ---
        self.scale_factor = WINDOW_SCALING
        ctk.set_widget_scaling(self.scale_factor)
        ctk.set_window_scaling(self.scale_factor)
        
        self.bind("<Control-plus>", lambda e: self.adjust_scale(0.25))
        self.bind("<Control-equal>", lambda e: self.adjust_scale(0.25))
        self.bind("<Control-minus>", lambda e: self.adjust_scale(-0.25))
        self.bind("<Control-0>", lambda e: self.reset_scale())
        self.bind("<Control-MouseWheel>", self.on_mousewheel_scale)
        
        self.title("Winding Visualisation")
        self.geometry("1200x750")
        self.minsize(1000, 700)
        self.configure(fg_color=Theme.BG_MAIN.value)
        ctk.set_appearance_mode("system")


        # --- LAYOUT GRID CONFIGURATION ---
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Core Workspace panels
        self.grid_columnconfigure(0, weight=1)

        # --- STATE INITIALIZATION ---
        self.language_var = ctk.StringVar(value="english")
        self.lang_manager = LanguageManager(default_lang="english")
        
        self.geometry_state = Geometry()
        self.winding_state = Winding()
        self.magnet= Magnet()
        self.operating_state = OperatingState()
        self.generator = Generator(self.geometry_state, self.winding_state, self.magnet, self.operating_state)

        # --- WIDGET CREATION ---
        self.create_header()

        mode_idx = 0 if ctk.get_appearance_mode() == "Light" else 1
        self.paned_window = tk.PanedWindow(
            self, 
            orient=tk.HORIZONTAL, 
            sashwidth=6,
            sashrelief=tk.FLAT,
            bg=Theme.BG_MAIN.get_color(),
            bd=0
        )
        self.paned_window.grid(row=1, column=0, sticky="nsew", padx=5, pady=(5, 10))

        # Instantiate modular panel frames
        self.console = ConsolePanel(self.paned_window, app=self)
        self.paned_window.add(self.console, minsize=380, stretch="never")

        self.cad_canvas = CADCanvas(self.paned_window, app=self)
        self.paned_window.add(self.cad_canvas, minsize=400, stretch="always")

        self.analytics = AnalyticsPanel(self.paned_window, app=self)
        self.paned_window.add(self.analytics, minsize=420, stretch="never")

        self.on_inputs_changed()
        self.update_language()

    def create_header(self):
        # Header main container
        self.header_frame = ctk.CTkFrame(
            self, 
            fg_color=Theme.BG_SURFACE.value, 
            corner_radius=0, 
            border_width=1, 
            border_color=Theme.BORDER.value
        )
        self.header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=(10, 5))
        
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=0)

        # Left Column: App Title
        left_header = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        left_header.grid(row=0, column=0, sticky="w", padx=15, pady=10)
        
        self.lbl_title = ctk.CTkLabel(
            left_header, 
            font=Theme.fonts.TITLE,
            text_color=Theme.ACCENT.value,
            padx=0,
            height=20
        )
        self.lbl_title.pack(anchor="w", pady=(2, 0))

        ToolTip(self.lbl_title, text="Configure in Settings, Wind the generator in Winding Layout, Simulate and view results in Overview and Overtones.")

        

        # Right Column: Theme selection & scale
        right_header = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        right_header.grid(row=0, column=1, sticky="e", padx=15, pady=10)


        # UI Scaling Dropdown
        scale_frame = ctk.CTkFrame(right_header, fg_color="transparent")
        scale_frame.pack(side="left", padx=(0, 15))
        self.lbl_zoom = ctk.CTkLabel(scale_frame, font=Theme.fonts.HEADER, text_color=Theme.TEXT_MUTED.value, height=12)
        self.lbl_zoom.pack(anchor="center", pady=(0, 4))
        self.scale_menu = ctk.CTkOptionMenu(
            scale_frame,
            values=["75%", "100%", "125%", "150%", "200%", "250%", "300%"],
            command=self.on_scale_dropdown,
            fg_color=Theme.BG_INPUT.value,
            button_color=Theme.BUTTON_BG.value,
            button_hover_color=Theme.BUTTON_HOVER.value,
            text_color=Theme.TEXT_MAIN.value,
            width=80,
            height=24,
            font=Theme.fonts.MUTED
        )
        self.scale_menu.pack(anchor="center")
        
        # Determine initial selection based on self.scale_factor
        pct = int(self.scale_factor * 100)
        closest = min([75, 100, 125, 150, 200, 250, 300], key=lambda x: abs(x - pct))
        self.scale_menu.set(f"{closest}%")

        # Theme Selector Dropdown
        theme_frame = ctk.CTkFrame(right_header, fg_color="transparent")
        theme_frame.pack(side="left", padx=(0, 15))
        self.lbl_theme = ctk.CTkLabel(theme_frame, font=Theme.fonts.HEADER, text_color=Theme.TEXT_MUTED.value, height=12)
        self.lbl_theme.pack(anchor="center", pady=(0, 4))
        self.theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["Dark", "Light", "System"],
            command=self.on_theme_change,
            fg_color=Theme.BG_INPUT.value,
            button_color=Theme.BUTTON_BG.value,
            button_hover_color=Theme.BUTTON_HOVER.value,
            text_color=Theme.TEXT_MAIN.value,
            width=90,
            height=24,
            font=Theme.fonts.MUTED
        )
        self.theme_menu.pack(anchor="center")
        self.theme_menu.set("System")
        self._current_theme_eng = "System"



        # Language Toggle
        lang_frame = ctk.CTkFrame(right_header, fg_color="transparent")
        lang_frame.pack(side="left", padx=(0, 15))
        self.lbl_lang = ctk.CTkLabel(lang_frame, font=Theme.fonts.HEADER, text_color=Theme.TEXT_MUTED.value, height=12)
        self.lbl_lang.pack(anchor="center", pady=(0, 4))
        
        # Load initial flag image to prevent CustomTkinter layout bugs where configure(image=...) fails
        flag_name = self.lang_manager.get("flag_icon")
        if flag_name:
            icon_path = self.lang_manager.get_asset_path(os.path.join("assets", "icons", flag_name))
            self.current_flag_img = ctk.CTkImage(
                light_image=Image.open(icon_path),
                size=(16, 16)
            )
        else:
            self.current_flag_img = None

        self.btn_language = ctk.CTkButton(
            lang_frame,
            text="",
            image=self.current_flag_img,
            command=self.toggle_language,
            width=30,
            height=24,
            fg_color=Theme.BG_INPUT.value,
            hover_color=Theme.BUTTON_HOVER.value,
        )
        self.btn_language.pack(anchor="center")

    def toggle_language(self):
        if self.language_var.get() == "english":
            self.language_var.set("swedish")
            self.lang_manager.load_language("swedish")
        else:
            self.language_var.set("english")
            self.lang_manager.load_language("english")
        self.update_language()

    def update_flag_button(self):
        flag_name = self.lang_manager.get("flag_icon")
        if flag_name:
            icon_path = self.lang_manager.get_asset_path(os.path.join("assets", "icons", flag_name))
            self.current_flag_img = ctk.CTkImage(
                light_image=Image.open(icon_path),
                size=(16, 16)
            )
            self.btn_language.configure(image=self.current_flag_img)

    def update_language(self):
        self.update_flag_button()
        
        # Update header labels
        self.lbl_title.configure(text=self.lang_manager.get("header.app_title"))
        self.lbl_zoom.configure(text=self.lang_manager.get("header.lbl_zoom"))
        self.lbl_theme.configure(text=self.lang_manager.get("header.lbl_theme"))
        self.lbl_lang.configure(text=self.lang_manager.get("header.lbl_lang"))
        
        # Update Theme Dropdown Option values
        themes = self.lang_manager.get("themes", {})
        self.theme_menu.configure(values=[themes.get(k, k) for k in ["Dark", "Light", "System"]])
        self._current_theme_eng = getattr(self, '_current_theme_eng', "System")
        self.theme_menu.set(themes.get(self._current_theme_eng, self._current_theme_eng))
        
        
        # Propagate to sub-panels if they exist
        if hasattr(self, "console"):
            self.console.update_language()
        if hasattr(self, "analytics"):
            self.analytics.update_language()
        if hasattr(self, "cad_canvas"):
            self.cad_canvas.update_language()

    def on_theme_change(self, choice: str):
        # Map translated dropdown name back to English key
        themes = self.lang_manager.get("themes", {})
        eng_val = next((eng for eng, tr in themes.items() if tr == choice), choice)
        
        self._current_theme_eng = eng_val
        ctk.set_appearance_mode(eng_val.lower())
        self.after(50, self.update_theme_drawings)

    def on_scale_dropdown(self, choice: str):
        pct = int(choice.replace("%", ""))
        self.apply_scale(pct / 100.0)

    def adjust_scale(self, delta):
        new_scale = self.scale_factor + delta
        self.apply_scale(new_scale)
        
    def reset_scale(self):
        self.apply_scale(WINDOW_SCALING)

    def on_mousewheel_scale(self, event):
        if event.delta > 0:
            self.adjust_scale(0.1)
        elif event.delta < 0:
            self.adjust_scale(-0.1)

    def apply_scale(self, new_scale):
        new_scale = max(0.5, min(new_scale, 3.5))
        if abs(new_scale - self.scale_factor) < 0.01:
            return
            
        self.scale_factor = new_scale
        pct = int(self.scale_factor * 100)
        
        closest = min([75, 100, 125, 150, 200, 250, 300], key=lambda x: abs(x - pct))
        self.scale_menu.set(f"{closest}%")
        
        ctk.set_widget_scaling(self.scale_factor)
        ctk.set_window_scaling(self.scale_factor)
        self.after(50, self.update_theme_drawings)

    def update_theme_drawings(self):
        self.configure(fg_color=Theme.BG_MAIN.value)
        self.paned_window.configure(bg=Theme.BG_MAIN.get_color())
        self.cad_canvas.update_geometry()
        self.console.update_from_models()
        self.analytics.update_theme()

    def on_inputs_changed(self):
        self.analytics.show_warning_banner(True)
        self.analytics.clear_charts()

    def run_simulation(self):
        # Disable controls during simulation
        self.console.set_inputs_enabled(False)
        self.analytics.show_loading(True, self.lang_manager.get("analytics.lbl_loading_status_init"))

        # Step-by-step loading progress animation
        self.after(500, lambda: self.analytics.set_loading_status(self.lang_manager.get("analytics.lbl_loading_status_solving")))
        self.after(1200, lambda: self.analytics.set_loading_status(self.lang_manager.get("analytics.lbl_loading_status_voltages")))
        self.after(2000, self.complete_simulation)

    def complete_simulation(self):
        self.console.set_inputs_enabled(True)
        
        dt, time_steps = create_steps(frequency=self.generator.frequency, nb_periods=NB_PERIODS, points_per_period=64)
        
        phase_voltages = SimulateGenerator.simulate(self.generator, time_steps)
        noised_phase_voltages = SimulateGenerator.apply_noise(self.generator, phase_voltages)
        
        self.analytics.draw_simulation_results(time_steps, noised_phase_voltages)
        self.analytics.draw_overtones_results(dt, self.generator.frequency, phase_voltages)