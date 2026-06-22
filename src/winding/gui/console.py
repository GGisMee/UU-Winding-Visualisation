import customtkinter as ctk
import tkinter as tk
from .theme import Theme
from .components import LabeledSlider, MetricRow, TextInfoBox

class ConsolePanel(ctk.CTkFrame):
    def __init__(self, parent, app=None):
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

        self.app = app
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
        self.settings_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Variables
        init_phases = self.app.winding_state.phases if self.app else 5
        init_poles = self.app.winding_state.poles if self.app else 4
        init_slots = self.app.winding_state.slots if self.app else 38
        init_rpm = self.app.operating_state.RPM if self.app else 240

        self.var_phases = ctk.DoubleVar(value=init_phases)
        self.var_poles = ctk.DoubleVar(value=init_poles)
        self.var_slots = ctk.DoubleVar(value=init_slots)
        self.var_rpm = ctk.DoubleVar(value=init_rpm)

        # Sliders
        self.slider_phases = LabeledSlider(
            self.settings_frame, "Phases: {value:.0f}", self.var_phases, 1, 10, 9, self.on_change_phases
        )
        self.slider_phases.pack(fill="x", pady=10)

        self.slider_poles = LabeledSlider(
            self.settings_frame, "Poles: {value:.0f}", self.var_poles, 2, 10, 4, self.on_change_poles
        )
        self.slider_poles.pack(fill="x", pady=10)

        self.slider_slots = LabeledSlider(
            self.settings_frame, "Slots: {value:.0f}", self.var_slots, 10, 100, 90, self.on_change_slots
        )
        self.slider_slots.pack(fill="x", pady=10)

        self.slider_rpm = LabeledSlider(
            self.settings_frame, "RPM: {value:.0f}", self.var_rpm, 10, 1000, 198, self.on_change_rpm
        )
        self.slider_rpm.pack(fill="x", pady=10)

        # Simulate Button
        self.btn_simulate = ctk.CTkButton(
            self.settings_frame, 
            text="Simulate", 
            font=Theme.fonts.BODY_BOLD,
            fg_color=Theme.BUTTON_BG.value,
            hover_color=Theme.BUTTON_HOVER.value,
            text_color=Theme.TEXT_MAIN.value,
            command=self.on_simulate
        )
        self.btn_simulate.pack(fill="x", pady=(20, 0))

    def on_change_phases(self, val):
        if self.app:
            self.app.winding_state.phases = int(val)
            self.app.winding_state.resize_matrix()
            self.app.cad_canvas.update_geometry()

    def on_change_poles(self, val):
        if self.app:
            self.app.winding_state.poles = int(val)
            self.app.winding_state.resize_matrix()
            self.app.cad_canvas.update_geometry()

    def on_change_slots(self, val):
        if self.app:
            self.app.winding_state.slots = int(val)
            self.app.winding_state.resize_matrix()
            self.app.cad_canvas.update_geometry()

    def on_change_rpm(self, val):
        if self.app:
            self.app.operating_state.RPM = int(val)

    def on_simulate(self):
        if self.app:
            import numpy as np
            from ..models.simulation import simulate_generator
            # Generate time steps for one full mechanical rotation at the given RPM
            # time_for_one_rot = 60.0 / max(1, self.app.operating_state.RPM)
            # time_steps = np.linspace(0, time_for_one_rot, 500)
            # Or just simulate a fixed 0.2 seconds like the original code
            time_steps = np.linspace(0, 0.2, 200)
            
            phase_voltages = simulate_generator(self.app.generator, time_steps)
            self.app.analytics.draw_simulation_results(time_steps, phase_voltages)

    def set_inputs_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self.slider_phases.configure_slider(state=state)
        self.slider_poles.configure_slider(state=state)
        self.slider_slots.configure_slider(state=state)
        self.slider_rpm.configure_slider(state=state)
        self.btn_simulate.configure(state=state)

    def update_from_models(self):
        if self.app:
            self.var_phases.set(self.app.winding_state.phases)
            self.slider_phases.update_label()
            self.var_poles.set(self.app.winding_state.poles)
            self.slider_poles.update_label()
            self.var_slots.set(self.app.winding_state.slots)
            self.slider_slots.update_label()
            self.var_rpm.set(self.app.operating_state.RPM)
            self.slider_rpm.update_label()