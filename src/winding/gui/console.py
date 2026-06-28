import customtkinter as ctk
import tkinter as tk
import numpy as np
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .theme import Theme
from .components import LabeledSlider, MetricRow, TextInfoBox, ToolTip

class MagnetPlotCard(ctk.CTkFrame):
    def __init__(self, master, var_magnet_type, app=None):
        super().__init__(master, fg_color="transparent")
        self.var_magnet_type = var_magnet_type
        self.app = app
        
        self.magnet_fig = Figure(figsize=(3, 2), dpi=100, constrained_layout=True)
        self.magnet_ax = self.magnet_fig.add_subplot(111)
        self.magnet_canvas = FigureCanvasTkAgg(self.magnet_fig, master=self)
        
        widget = self.magnet_canvas.get_tk_widget()
        widget.pack(fill="x", pady=(0, 10))

    def update_plot(self):
        self.magnet_ax.clear()
        
        bg_color = Theme.BG_SURFACE.get_color()
        text_color = Theme.TEXT_MAIN.get_color()
        border_color = Theme.BORDER.get_color()
        accent_color = Theme.ACCENT.get_color()
        
        self.magnet_fig.patch.set_facecolor(bg_color)
        self.magnet_ax.set_facecolor(bg_color)
        
        self.magnet_ax.set_xticks([])
        self.magnet_ax.set_yticks([])
        self.magnet_ax.spines["top"].set_visible(False)
        self.magnet_ax.spines["right"].set_visible(False)
        self.magnet_ax.spines["left"].set_visible(False)
        self.magnet_ax.spines["bottom"].set_color(border_color)
            
        x = np.linspace(0, 2*np.pi, 200)
        try:
            from ..models.magnets import MagnetFunction
            y = MagnetFunction[self.var_magnet_type.get().replace(" ", "_")].value(x)
            
            self.magnet_ax.plot(x, y, color=accent_color, linewidth=2)
            self.magnet_ax.fill_between(x, y, 0, color=accent_color, alpha=0.15)
            self.magnet_ax.axhline(0, color=border_color, linewidth=1, linestyle="--")
            
            self.magnet_ax.set_box_aspect(2/3)
            
            self.magnet_ax.set_ylim(-1.2, 1.2)
            self.magnet_ax.set_xlim(0, 2*np.pi)
            title = self.app.lang_manager.get("console.lbl_field_profile", "Field Profile") if self.app else "Field Profile"
            self.magnet_ax.set_title(title, color=text_color, fontsize=12, pad=5)
        except Exception as e:
            print("ERROR IN PLOT:", e)
            import traceback
            traceback.print_exc()
        self.magnet_canvas.draw()


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
        init_positions = self.app.winding_state.positions if self.app else 4
        init_slots = self.app.winding_state.slots if self.app else 38
        init_rpm = self.app.operating_state.RPM if self.app else 240
        init_magnet = self.app.generator.magnet.magnet_function.name.replace("_", " ") if self.app else "Smooth Square"

        self.var_phases = ctk.DoubleVar(value=init_phases)
        self.var_poles = ctk.DoubleVar(value=init_poles)
        self.var_positions = ctk.DoubleVar(value=init_positions)
        self.var_slots = ctk.DoubleVar(value=init_slots)
        self.var_rpm = ctk.DoubleVar(value=init_rpm)
        self.var_magnet_type = ctk.StringVar(value=init_magnet)

        # Sliders
        self.slider_phases = LabeledSlider(
            self.settings_frame, "Phases: {value:.0f}", self.var_phases, 1, 10, 9, self.on_change_phases,
            tooltip_text="The number of electrical phases (e.g. 3-phase or 5-phase)."
        )
        self.slider_phases.pack(fill="x", pady=10)

        self.slider_poles = LabeledSlider(
            self.settings_frame, "Poles: {value:.0f}", self.var_poles, 2, 10, 4, self.on_change_poles,
            tooltip_text="The number of magnetic poles in the rotor."
        )
        self.slider_poles.pack(fill="x", pady=10)

        self.slider_positions = LabeledSlider(
            self.settings_frame, "Positions: {value:.0f}", self.var_positions, 1, 10, 9, self.on_change_positions,
            tooltip_text="The number of winding positions (layers) per slot."
        )
        self.slider_positions.pack(fill="x", pady=10)

        self.slider_slots = LabeledSlider(
            self.settings_frame, "Slots: {value:.0f}", self.var_slots, 10, 100, 90, self.on_change_slots,
            tooltip_text="The number of slots in the stator."
        )
        self.slider_slots.pack(fill="x", pady=10)

        self.slider_rpm = LabeledSlider(
            self.settings_frame, "RPM: {value:.0f}", self.var_rpm, 10, 1000, 198, self.on_change_rpm,
            tooltip_text="The rotational speed of the generator in revolutions per minute."
        )
        self.slider_rpm.pack(fill="x", pady=10)

        # --- Magnet Function ---
        self.lbl_magnet = ctk.CTkLabel(self.settings_frame, text="Magnet Function", font=Theme.fonts.BODY_BOLD, text_color=Theme.TEXT_MAIN.value)
        self.lbl_magnet.pack(anchor="w", pady=(10, 5))
        ToolTip(self.lbl_magnet, "The shape of the magnetic field.", small=True)
        self.magnet_menu = ctk.CTkOptionMenu(
            self.settings_frame,
            values=["Smooth Square", "Sharp Square", "Rounded Triangle"],
            variable=self.var_magnet_type,
            command=self.on_change_magnet_type,
            fg_color=Theme.BG_INPUT.value,
            button_color=Theme.BUTTON_BG.value,
            button_hover_color=Theme.BUTTON_HOVER.value,
            text_color=Theme.TEXT_MAIN.value
        )
        self.magnet_menu.pack(fill="x", pady=(0, 10))
        
        self.magnet_plot_card = MagnetPlotCard(self.settings_frame, self.var_magnet_type, app=self.app)
        self.magnet_plot_card.pack(fill="x")
        self.magnet_plot_card.update_plot()

        # Simulate Button
        self.btn_simulate = ctk.CTkButton(
            self.settings_frame, 
            text="Simulate", 
            font=Theme.fonts.BODY_BOLD,
            fg_color=Theme.BUTTON_BG.value,
            hover_color=Theme.BUTTON_HOVER.value,
            text_color=Theme.TEXT_MAIN.value,
            command=self.app.run_simulation if self.app else None
        )
        self.btn_simulate.pack(fill="x", pady=(15, 0))

    def on_change_phases(self, val):
        if self.app:
            self.app.winding_state.phases = int(val)
            self.app.winding_state.resize_matrix()
            self.app.cad_canvas.update_geometry()
            if hasattr(self.app, 'on_inputs_changed'):
                self.app.on_inputs_changed()

    def on_change_poles(self, val):
        if self.app:
            self.app.winding_state.poles = int(val)
            if hasattr(self.app, 'on_inputs_changed'):
                self.app.on_inputs_changed()

    def on_change_positions(self, val):
        if self.app:
            self.app.winding_state.positions = int(val)
            self.app.winding_state.resize_matrix()
            self.app.cad_canvas.update_geometry()
            if hasattr(self.app, 'on_inputs_changed'):
                self.app.on_inputs_changed()

    def on_change_slots(self, val):
        if self.app:
            self.app.winding_state.slots = int(val)
            self.app.winding_state.resize_matrix()
            self.app.cad_canvas.update_geometry()
            if hasattr(self.app, 'on_inputs_changed'):
                self.app.on_inputs_changed()

    def on_change_rpm(self, val):
        if self.app:
            self.app.operating_state.RPM = int(val)
            if hasattr(self.app, 'on_inputs_changed'):
                self.app.on_inputs_changed()

    def on_change_magnet_type(self, val):
        if self.app:
            # Map translated dropdown name back to English key
            magnet_types = self.app.lang_manager.get("magnet_types", {})
            eng_val = next((eng for eng, tr in magnet_types.items() if tr == val), val)
            
            from ..models.magnets import MagnetFunction
            self.app.generator.magnet.magnet_function = MagnetFunction[eng_val.replace(" ", "_")]
            if hasattr(self.app, 'on_inputs_changed'):
                self.app.on_inputs_changed()
        self.magnet_plot_card.update_plot()



    def set_inputs_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self.slider_phases.configure_slider(state=state)
        self.slider_poles.configure_slider(state=state)
        self.slider_positions.configure_slider(state=state)
        self.slider_slots.configure_slider(state=state)
        self.slider_rpm.configure_slider(state=state)
        self.magnet_menu.configure(state=state)
        self.btn_simulate.configure(state=state)

    def update_from_models(self):
        if self.app:
            self.var_phases.set(self.app.winding_state.phases)
            self.slider_phases.update_label()
            self.var_poles.set(self.app.winding_state.poles)
            self.slider_poles.update_label()
            self.var_positions.set(self.app.winding_state.positions)
            self.slider_positions.update_label()
            self.var_slots.set(self.app.winding_state.slots)
            self.slider_slots.update_label()
            self.var_rpm.set(self.app.operating_state.RPM)
            self.slider_rpm.update_label()
            eng_val = self.app.generator.magnet.magnet_function.name.replace("_", " ")
            translated_val = self.app.lang_manager.get(f"magnet_types.{eng_val}", eng_val)
            self.var_magnet_type.set(translated_val)
            self.magnet_plot_card.update_plot()

    def update_language(self):
        if not self.app:
            return
            
        # Update Title & static labels
        self.lbl_title.configure(text=self.app.lang_manager.get("console.title"))
        self.lbl_magnet.configure(text=self.app.lang_manager.get("console.lbl_magnet"))
        self.btn_simulate.configure(text=self.app.lang_manager.get("console.btn_simulate"))
        
        # Update Tab
        if hasattr(self.tabs, "_segmented_button") and hasattr(self.tabs._segmented_button, "_buttons_dict"):
            buttons_dict = self.tabs._segmented_button._buttons_dict
            if "Settings" in buttons_dict:
                buttons_dict["Settings"].configure(text=self.app.lang_manager.get("tabs.settings", "Settings"))
        
        # Update Sliders
        self.slider_phases.update_label_template(self.app.lang_manager.get("console.slider_phases"))
        self.slider_poles.update_label_template(self.app.lang_manager.get("console.slider_poles"))
        self.slider_positions.update_label_template(self.app.lang_manager.get("console.slider_positions"))
        self.slider_slots.update_label_template(self.app.lang_manager.get("console.slider_slots"))
        self.slider_rpm.update_label_template(self.app.lang_manager.get("console.slider_rpm"))
        
        # Update Magnet Dropdown Option values
        magnet_types = self.app.lang_manager.get("magnet_types", {})
        self.magnet_menu.configure(values=list(magnet_types.values()))
        current_eng = self.app.generator.magnet.magnet_function.name.replace("_", " ")
        self.var_magnet_type.set(magnet_types.get(current_eng, current_eng))