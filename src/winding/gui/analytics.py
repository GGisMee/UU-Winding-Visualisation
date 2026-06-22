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

    def draw_simulation_results(self, time_steps, phase_voltages):
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

    def draw_performance_curves(self):
        pass

    def redraw_capex_bar(self):
        pass