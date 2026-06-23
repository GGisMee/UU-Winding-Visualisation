import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .theme import Theme

class AnalyticsPanel(ctk.CTkFrame):
    def __init__(self, parent, app=None):
        super().__init__(
            parent, 
            width=420, 
            fg_color=Theme.BG_SURFACE.value, 
            border_width=1, 
            border_color=Theme.BORDER.value
        )
        # Prevent auto-shrinking
        self.pack_propagate(False)
        self.grid_propagate(False)

        self.app = app

        # Title Label
        self.lbl_title = ctk.CTkLabel(
            self, 
            text="ANALYTICS & RESULTS", 
            font=Theme.fonts.SUBTITLE, 
            text_color=Theme.TEXT_ACCENT.value
        )
        self.lbl_title.pack(anchor="w", padx=15, pady=(15, 5))

        # Main Tabview
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
        
        self.tabs.add("Overview")

        mode_idx = 0 if ctk.get_appearance_mode() == "Light" else 1
        bg_color = Theme.BG_SURFACE.value[mode_idx]
        text_color = Theme.TEXT_MAIN.value[mode_idx]
        border_color = Theme.BORDER.value[mode_idx]

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.figure.patch.set_facecolor(bg_color)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(bg_color)
        self.ax.tick_params(colors=text_color)
        self.ax.xaxis.label.set_color(text_color)
        self.ax.yaxis.label.set_color(text_color)
        for spine in self.ax.spines.values():
            spine.set_color(border_color)
            
        self.ax.set_title("Phase Voltages Over Time", color=text_color)
        self.ax.set_xlabel("Time [s]")
        self.ax.set_ylabel("Voltage [V]")

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.tabs.tab("Overview"))
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

        # ==========================================
        # WARNING BANNER & LOADING OVERLAY
        # ==========================================
        # Warning Banner (shown when inputs change, prompting rerun)
        self.warning_banner = ctk.CTkFrame(self, fg_color=Theme.ALERT_BG.value, height=32, corner_radius=0)
        self.lbl_warning = ctk.CTkLabel(
            self.warning_banner, 
            text="⚠️ Inputs changed. Click 'Simulate' to recalculate results.",
            font=Theme.fonts.BODY_BOLD,
            text_color=Theme.ALERT.value
        )
        self.lbl_warning.pack(pady=4)

        # Loading Overlay (covers entire panel during simulation run)
        self.loading_overlay = ctk.CTkFrame(self, fg_color=Theme.BG_SURFACE.value, corner_radius=0)
        self.loading_container = ctk.CTkFrame(self.loading_overlay, fg_color=Theme.BG_SURFACE.value)
        self.loading_container.place(relx=0.5, rely=0.45, anchor="center")

        lbl = ctk.CTkLabel(
            self.loading_container, 
            text="SIMULATION RUNNING", 
            font=Theme.fonts.SUBTITLE, 
            text_color=Theme.ACCENT.value
        )
        lbl.pack(pady=5)
        
        self.lbl_loading_status = ctk.CTkLabel(
            self.loading_container, 
            text="Initializing generator model...", 
            font=Theme.fonts.BODY, 
            text_color=Theme.TEXT_MAIN.value
        )
        self.lbl_loading_status.pack(pady=(0, 15))

        self.loading_progress = ctk.CTkProgressBar(
            self.loading_container, 
            width=280, 
            progress_color=Theme.ACCENT.value, 
            fg_color=Theme.BG_MAIN.value
        )
        self.loading_progress.pack()

        # Initial clean view
        self.clear_charts()
        self.show_warning_banner(False)

    def show_warning_banner(self, show: bool):
        if show:
            self.warning_banner.place(relx=0, rely=0.92, relwidth=1, relheight=0.08)
        else:
            self.warning_banner.place_forget()

    def show_loading(self, show: bool, message: str = ""):
        if show:
            self.loading_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.loading_progress.start()
            if message:
                self.lbl_loading_status.configure(text=message)
        else:
            self.loading_progress.stop()
            self.loading_overlay.place_forget()

    def set_loading_status(self, text: str):
        self.lbl_loading_status.configure(text=text)

    def clear_charts(self):
        self.ax.clear()
        mode_idx = 0 if ctk.get_appearance_mode() == "Light" else 1
        bg_color = Theme.BG_SURFACE.value[mode_idx]
        muted_color = Theme.TEXT_MUTED.value[mode_idx]

        self.figure.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)
        self.ax.text(0.5, 0.5, "[ Simulation Out of Date ]\nClick 'Simulate' to plot curves.",
                ha='center', va='center', color=muted_color, fontweight='bold', fontsize=12)
        self.ax.axis('off')
        self.canvas.draw()


    def draw_simulation_results(self, time_steps, phase_voltages):
        self.show_warning_banner(False)
        self.show_loading(False)
        self.ax.clear()

        mode_idx = 0 if ctk.get_appearance_mode() == "Light" else 1
        bg_color = Theme.BG_SURFACE.value[mode_idx]
        text_color = Theme.TEXT_MAIN.value[mode_idx]
        border_color = Theme.BORDER.value[mode_idx]

        self.figure.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)
        self.ax.tick_params(colors=text_color)
        self.ax.xaxis.label.set_color(text_color)
        self.ax.yaxis.label.set_color(text_color)
        for spine in self.ax.spines.values():
            spine.set_color(border_color)
            
        self.ax.set_title("Phase Voltages Over Time", color=text_color)
        self.ax.set_xlabel("Time [s]")
        self.ax.set_ylabel("Voltage [V]")

        phase_colors = ["#EF4444", "#3B82F6", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899", "#06B6D4", "#F97316", "#84CC16", "#6366F1"]

        for phase_idx in range(phase_voltages.shape[0]):
            color = phase_colors[phase_idx % len(phase_colors)]
            self.ax.plot(time_steps, phase_voltages[phase_idx, :], label=f"Phase {phase_idx + 1}", color=color)
            
        self.ax.legend(facecolor=bg_color, edgecolor=border_color, labelcolor=text_color, loc='upper right')
        self.ax.grid(True, linestyle='--', alpha=0.6, color=border_color)
        
        self.canvas.draw()
