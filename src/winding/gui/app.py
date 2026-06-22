import os
import customtkinter as ctk
import tkinter as tk
from .console import ConsolePanel
from .canvas import CADCanvas
from .analytics import AnalyticsPanel
from .theme import Theme


def load_scale_factor():
    try:
        dir_path = os.path.dirname(os.path.abspath(__file__))
        scale_path = os.path.join(dir_path, "scale.txt")
        if os.path.exists(scale_path):
            with open(scale_path, "r") as f:
                return float(f.read().strip())
    except Exception:
        pass
        
    import platform
    if platform.system() == "Linux":
        try:
            import tkinter as tk
            temp_root = tk.Tk()
            temp_root.withdraw()
            dpi = temp_root.winfo_fpixels('1i')
            temp_root.destroy()
            scale = dpi / 96.0
            return max(1.0, min(scale, 3.0))
        except Exception:
            pass

    return 1.0


class UnifiedSimulatorApp(ctk.CTk):
    def __init__(self):
        super().__init__(className="main")

        # --- SCALING & LOOK SETUP ---
        self.scale_factor = load_scale_factor()
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

        # --- WIDGET CREATION ---
        self.create_header()

        mode_idx = 0 if ctk.get_appearance_mode() == "Light" else 1
        self.paned_window = tk.PanedWindow(
            self, 
            orient=tk.HORIZONTAL, 
            sashwidth=6,
            sashrelief=tk.FLAT,
            bg=Theme.BG_MAIN.value[mode_idx],
            bd=0
        )
        self.paned_window.grid(row=1, column=0, sticky="nsew", padx=5, pady=(5, 10))

        # Instantiate modular panel frames
        self.console = ConsolePanel(self.paned_window)
        self.paned_window.add(self.console, minsize=380, stretch="never")

        self.cad_canvas = CADCanvas(self.paned_window)
        self.paned_window.add(self.cad_canvas, minsize=400, stretch="always")

        self.analytics = AnalyticsPanel(self.paned_window)
        self.paned_window.add(self.analytics, minsize=420, stretch="never")

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
            text="Application",
            font=Theme.fonts.TITLE,
            text_color=Theme.ACCENT.value,
            padx=0,
            height=20
        )
        self.lbl_title.pack(anchor="w", pady=(2, 0))

        # Right Column: Theme selection & scale
        right_header = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        right_header.grid(row=0, column=1, sticky="e", padx=15, pady=10)

        # UI Scaling Dropdown
        scale_frame = ctk.CTkFrame(right_header, fg_color="transparent")
        scale_frame.pack(side="left", padx=(0, 15))
        ctk.CTkLabel(scale_frame, text="ZOOM", font=Theme.fonts.HEADER, text_color=Theme.TEXT_MUTED.value).pack(anchor="w")
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
        self.scale_menu.pack(anchor="w")
        
        # Determine initial selection based on self.scale_factor
        pct = int(self.scale_factor * 100)
        closest = min([75, 100, 125, 150, 200, 250, 300], key=lambda x: abs(x - pct))
        self.scale_menu.set(f"{closest}%")

        # Theme Selector Dropdown
        theme_frame = ctk.CTkFrame(right_header, fg_color="transparent")
        theme_frame.pack(side="left", padx=(0, 15))
        ctk.CTkLabel(theme_frame, text="THEME", font=Theme.fonts.HEADER, text_color=Theme.TEXT_MUTED.value).pack(anchor="w")
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
        self.theme_menu.pack(anchor="w")
        self.theme_menu.set("System")

    def on_theme_change(self, choice: str):
        ctk.set_appearance_mode(choice.lower())
        self.after(50, self.update_theme_drawings)

    def on_scale_dropdown(self, choice: str):
        pct = int(choice.replace("%", ""))
        self.apply_scale(pct / 100.0)

    def adjust_scale(self, delta):
        new_scale = self.scale_factor + delta
        self.apply_scale(new_scale)
        
    def reset_scale(self):
        self.apply_scale(load_scale_factor())

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
        mode_idx = 0 if ctk.get_appearance_mode() == "Light" else 1
        self.paned_window.configure(bg=Theme.BG_MAIN.value[mode_idx])
        self.cad_canvas.update_geometry()
        self.console.update_from_models()
        self.analytics.draw_performance_curves()
        self.analytics.redraw_capex_bar()