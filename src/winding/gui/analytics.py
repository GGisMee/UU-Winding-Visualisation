import customtkinter as ctk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .theme import Theme
from ..models.simulation import SimulateGenerator, PostProcess

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
        
        self.is_out_of_date = True
        self.current_time_steps = None
        self.current_phase_voltages = None
        self.current_dt = None
        self.current_fundamental_frequency = None

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
        self.tabs.add("Overtones")
        
        # Overtones Table container
        self.overtones_frame = ctk.CTkFrame(self.tabs.tab("Overtones"), fg_color="transparent")
        self.overtones_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

        bg_color = Theme.BG_SURFACE.get_color()
        text_color = Theme.TEXT_MAIN.get_color()
        border_color = Theme.BORDER.get_color()

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

        self.table_frame = ctk.CTkFrame(self.tabs.tab("Overview"), fg_color="transparent")
        self.table_frame.pack(side=ctk.BOTTOM, fill=ctk.X, padx=10, pady=10)

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

    def update_theme(self):
        if self.is_out_of_date:
            self.clear_charts()
        elif self.current_phase_voltages is not None:
            self.draw_simulation_results(self.current_time_steps, self.current_phase_voltages)
            self.draw_overtones_results(self.current_dt, self.current_fundamental_frequency, self.current_phase_voltages)

    def clear_charts(self):
        self.is_out_of_date = True
        self.ax.clear()
        bg_color = Theme.BG_SURFACE.get_color()
        muted_color = Theme.TEXT_MUTED.get_color()

        self.figure.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)
        self.ax.text(0.5, 0.5, "[ Simulation Out of Date ]\nClick 'Simulate' to plot curves.",
                ha='center', va='center', color=muted_color, fontweight='bold', fontsize=12)
        self.ax.axis('off')
        self.canvas.draw()

        for widget in self.table_frame.winfo_children():
            widget.destroy()
        lbl = ctk.CTkLabel(self.table_frame, text="Simulation out of date. Table will appear here.", text_color=Theme.TEXT_MUTED.value)
        lbl.pack(pady=10)
        
        for widget in self.overtones_frame.winfo_children():
            widget.destroy()
        lbl_ot = ctk.CTkLabel(self.overtones_frame, text="Simulation out of date. Table will appear here.", text_color=Theme.TEXT_MUTED.value)
        lbl_ot.pack(pady=10)

    def draw_simulation_results(self, time_steps, phase_voltages):
        self.is_out_of_date = False
        self.current_time_steps = time_steps
        self.current_phase_voltages = phase_voltages
        
        self.show_warning_banner(False)
        self.show_loading(False)
        self.ax.clear()

        bg_color = Theme.BG_SURFACE.get_color()
        text_color = Theme.TEXT_MAIN.get_color()
        border_color = Theme.BORDER.get_color()

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

        phase_colors = Theme.PHASE_COLORS.value


        for phase_idx in range(phase_voltages.shape[0]):
            color = phase_colors[phase_idx % len(phase_colors)]
            self.ax.plot(time_steps, phase_voltages[phase_idx, :], label=f"Phase {phase_idx + 1}", color=color)

        self.ax.plot(time_steps, np.sum(phase_voltages, axis=0), label="Sum of phase voltages", color="Black")

        self.ax.legend(facecolor=bg_color, edgecolor=border_color, labelcolor=text_color, loc='upper right')
        self.ax.grid(True, linestyle='--', alpha=0.6, color=border_color)
        
        self.canvas.draw()
        self.update_windings_table()

    def update_windings_table(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()
            
        if not self.app or not getattr(self.app, 'generator', None):
            return
            
        from .components import DataTable
        generator = self.app.generator
        total, up, down = SimulateGenerator.get_total_windings_per_phase(generator.wind.phases, generator.wind.winding_matrix)

        headers = ["Phase", "Total Windings", "Up", "Down"]
        tooltips = ["Electrical phase", "Total number of windings for this phase", "Number of windings with positive polarity", "Number of windings with negative polarity"]
        table = DataTable(self.table_frame, headers=headers, header_tooltips=tooltips)
        table.pack(fill=ctk.X, expand=True, pady=5)
        
        phase_colors = Theme.PHASE_COLORS.value
        
        for phase_idx in range(generator.wind.phases):
            row = phase_idx + 1
            p_color = phase_colors[phase_idx % len(phase_colors)]
            
            table.add_row(
                row_data=[f"Phase {row}", total[phase_idx], up[phase_idx], down[phase_idx]],
                text_colors=[p_color, None, None, None]
            )

        table.add_row(
            row_data=["Total", total.sum(), up.sum(), down.sum()],
            text_colors=[None, None, None, None],
            is_summary=True
        )

    def draw_overtones_results(self, dt, fundamental_frequency, phase_voltages):
        self.current_dt = dt
        self.current_fundamental_frequency = fundamental_frequency
        
        for widget in self.overtones_frame.winfo_children():
            widget.destroy()
            
        overtone_magnitudes = PostProcess.harmonics(dt, fundamental_frequency, phase_voltages)
        
        thd_values = PostProcess.THD(overtone_magnitudes)

        from .components import DataTable
        
        headers = ["Phase", "1st (f0)", "3rd (3f0)", "5th (5f0)", "7th (7f0)", "THD"]
        tooltips = ["Electrical phase", "Fundamental harmonic magnitude", "Third harmonic magnitude", "Fifth harmonic magnitude", "Seventh harmonic magnitude", "Total Harmonic Distortion (THD)"]
        table = DataTable(self.overtones_frame, headers=headers, header_tooltips=tooltips)
        table.pack(fill=ctk.X, expand=True, pady=5)
        
        phase_colors =Theme.PHASE_COLORS.value
        
        for phase_idx in range(phase_voltages.shape[0]):
            row = phase_idx + 1
            p_color = phase_colors[phase_idx % len(phase_colors)]
            mags = overtone_magnitudes[phase_idx]
            thd = thd_values[phase_idx]
            
            table.add_row(
                row_data=[f"Phase {row}", f"{mags[0]:.2f} V", f"{mags[1]:.2f} V", f"{mags[2]:.2f} V", f"{mags[3]:.2f} V", f"{thd*100:.2f} %"],
                text_colors=[p_color, None, None, None, None, None]
            )
