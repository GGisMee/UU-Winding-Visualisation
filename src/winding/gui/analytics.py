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

        # 1. Header Frame
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent", height=36)
        self.header_frame.pack(fill="x", padx=15, pady=(15, 5))

        # Title Label inside Header Frame
        self.lbl_title = ctk.CTkLabel(
            self.header_frame, 
            text="ANALYTICS & RESULTS", 
            font=Theme.fonts.SUBTITLE, 
            text_color=Theme.TEXT_ACCENT.value
        )
        self.lbl_title.pack(side="left")

        # Export Button inside Header Frame, right-aligned
        self.btn_export = ctk.CTkButton(
            self.header_frame, 
            text="Export", 
            font=Theme.fonts.BODY_BOLD,
            fg_color=Theme.BUTTON_BG.value, 
            hover_color=Theme.BUTTON_HOVER.value,
            text_color=Theme.TEXT_MAIN.value,
            width=120,
            height=28,
            command=getattr(self.app, 'export_results', None) if self.app else None
        )
        self.btn_export.pack(side="right")

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

        self.lbl_loading = ctk.CTkLabel(
            self.loading_container, 
            text="SIMULATION RUNNING", 
            font=Theme.fonts.SUBTITLE, 
            text_color=Theme.ACCENT.value
        )
        self.lbl_loading.pack(pady=5)
        
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
        msg = self.app.lang_manager.get("analytics.chart_out_of_date") if self.app else "[ Simulation Out of Date ]\nClick 'Simulate' to plot curves."
        self.ax.text(0.5, 0.5, msg,
                ha='center', va='center', color=muted_color, fontweight='bold', fontsize=12)
        self.ax.axis('off')
        self.canvas.draw()

        msg_tbl = self.app.lang_manager.get("analytics.table_out_of_date") if self.app else "Simulation out of date. Table will appear here."
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        lbl = ctk.CTkLabel(self.table_frame, text=msg_tbl, text_color=Theme.TEXT_MUTED.value)
        lbl.pack(pady=10)
        
        for widget in self.overtones_frame.winfo_children():
            widget.destroy()
        lbl_ot = ctk.CTkLabel(self.overtones_frame, text=msg_tbl, text_color=Theme.TEXT_MUTED.value)
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
            
        title = self.app.lang_manager.get("analytics.chart_title") if self.app else "Phase Voltages Over Time"
        xlabel = self.app.lang_manager.get("analytics.xlabel") if self.app else "Time [s]"
        ylabel = self.app.lang_manager.get("analytics.ylabel") if self.app else "Voltage [V]"
        self.ax.set_title(title, color=text_color)
        self.ax.set_xlabel(xlabel, color=text_color)
        self.ax.set_ylabel(ylabel, color=text_color)

        phase_colors = Theme.PHASE_COLORS.value


        phase_label_fmt = self.app.lang_manager.get("table_windings.phase_row") if self.app else "Phase {row}"
        for phase_idx in range(phase_voltages.shape[0]):
            color = phase_colors[phase_idx % len(phase_colors)]
            self.ax.plot(time_steps, phase_voltages[phase_idx, :], label=phase_label_fmt.format(row=phase_idx + 1), color=color)

        sum_label = self.app.lang_manager.get("analytics.chart_sum", "Sum of phase voltages") if self.app else "Sum of phase voltages"
        self.ax.plot(time_steps, np.sum(phase_voltages, axis=0), label=sum_label, color="Black")

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

        headers = self.app.lang_manager.get("table_windings.headers") if self.app else ["Phase", "Total Windings", "Up", "Down"]
        tooltips = self.app.lang_manager.get("table_windings.tooltips") if self.app else ["Electrical phase", "Total number of windings for this phase", "Number of windings with positive polarity", "Number of windings with negative polarity"]
        table = DataTable(self.table_frame, headers=headers, header_tooltips=tooltips)
        table.pack(fill=ctk.X, expand=True, pady=5)
        
        phase_colors = Theme.PHASE_COLORS.value
        
        phase_label_fmt = self.app.lang_manager.get("table_windings.phase_row") if self.app else "Phase {row}"
        self.windings_table_data = {"headers": headers, "rows": []}

        for phase_idx in range(generator.wind.phases):
            row = phase_idx + 1
            p_color = phase_colors[phase_idx % len(phase_colors)]
            row_data = [phase_label_fmt.format(row=row), total[phase_idx], up[phase_idx], down[phase_idx]]
            
            table.add_row(
                row_data=row_data,
                text_colors=[p_color, None, None, None]
            )
            self.windings_table_data["rows"].append(row_data)

        total_lbl = self.app.lang_manager.get("table_windings.total_row", "Total") if self.app else "Total"
        summary_row = [total_lbl, total.sum(), up.sum(), down.sum()]
        table.add_row(
            row_data=summary_row,
            text_colors=[None, None, None, None],
            is_summary=True
        )
        self.windings_table_data["rows"].append(summary_row)

    def draw_overtones_results(self, dt, fundamental_frequency, phase_voltages):
        self.current_dt = dt
        self.current_fundamental_frequency = fundamental_frequency
        
        for widget in self.overtones_frame.winfo_children():
            widget.destroy()
            
        overtone_magnitudes = PostProcess.harmonics(dt, fundamental_frequency, phase_voltages)
        thd_values = PostProcess.THD(overtone_magnitudes)
        self.avg_thd = np.mean(thd_values) 
        self.overtone_avg = np.mean(overtone_magnitudes, axis=0)
        
        self.current_overtone_magnitudes = overtone_magnitudes
        self.current_thd_values = thd_values

        from .components import DataTable
        
        headers = self.app.lang_manager.get("table_harmonics.headers") if self.app else ["Phase", "1st (f0)", "3rd (3f0)", "5th (5f0)", "7th (7f0)", "THD"]
        tooltips = self.app.lang_manager.get("table_harmonics.tooltips") if self.app else ["Electrical phase", "Fundamental harmonic magnitude", "Third harmonic magnitude", "Fifth harmonic magnitude", "Seventh harmonic magnitude", "Total Harmonic Distortion (THD)"]
        table = DataTable(self.overtones_frame, headers=headers, header_tooltips=tooltips)
        table.pack(fill=ctk.X, expand=True, pady=5)
        
        phase_colors =Theme.PHASE_COLORS.value
        
        phase_label_fmt = self.app.lang_manager.get("table_windings.phase_row") if self.app else "Phase {row}"
        self.overtones_table_data = {"headers": headers, "rows": []}

        for phase_idx in range(phase_voltages.shape[0]):
            row = phase_idx + 1
            p_color = phase_colors[phase_idx % len(phase_colors)]
            mags = overtone_magnitudes[phase_idx]
            thd = thd_values[phase_idx]
            
            row_data = [phase_label_fmt.format(row=row), f"{mags[0]:.2f} V", f"{mags[1]:.2f} V", f"{mags[2]:.2f} V", f"{mags[3]:.2f} V", f"{thd*100:.2f} %"]
            
            table.add_row(
                row_data=row_data,
                text_colors=[p_color, None, None, None, None, None]
            )
            self.overtones_table_data["rows"].append(row_data)

        avg_lbl = self.app.lang_manager.get("table_harmonics.average_row", "Average") if self.app else "Average"
        avg_mags = self.overtone_avg
        avg_thd = self.avg_thd
        
        avg_row = [
            avg_lbl, 
            f"{avg_mags[0]:.2f} V", 
            f"{avg_mags[1]:.2f} V", 
            f"{avg_mags[2]:.2f} V", 
            f"{avg_mags[3]:.2f} V", 
            f"{avg_thd*100:.2f} %"
        ]
        
        table.add_row(
            row_data=avg_row,
            text_colors=[None, None, None, None, None, None],
            is_summary=True
        )
        self.overtones_table_data["rows"].append(avg_row)

    def update_language(self):
        if not self.app:
            return
            
        # Update main Title, export button & warning banners
        self.lbl_title.configure(text=self.app.lang_manager.get("analytics.title"))
        self.btn_export.configure(text=self.app.lang_manager.get("analytics.btn_export", "Export"))
        self.lbl_warning.configure(text=self.app.lang_manager.get("analytics.lbl_warning"))
        self.lbl_loading.configure(text=self.app.lang_manager.get("analytics.lbl_loading"))
        
        # Update Tabs
        if hasattr(self.tabs, "_segmented_button") and hasattr(self.tabs._segmented_button, "_buttons_dict"):
            buttons_dict = self.tabs._segmented_button._buttons_dict
            if "Overview" in buttons_dict:
                buttons_dict["Overview"].configure(text=self.app.lang_manager.get("tabs.overview", "Overview"))
            if "Overtones" in buttons_dict:
                buttons_dict["Overtones"].configure(text=self.app.lang_manager.get("tabs.overtones", "Overtones"))

        # Redraw charts and tables in the newly loaded language
        self.update_theme()
