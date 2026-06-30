import customtkinter as ctk
import tkinter as tk
from .theme import Theme
from .components import ToolTip

class CADCanvas(ctk.CTkFrame):
    def __init__(self, parent, app=None):
        super().__init__(
            parent, 
            fg_color=Theme.BG_SURFACE.value, 
            border_width=1, 
            border_color=Theme.BORDER.value
        )
        
        self.app = app
        # Get parent scale factor if set
        self.scale_factor = getattr(parent, "scale_factor", 1.0)

        # Title Label
        self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.title_frame.pack(fill="x", padx=15, pady=(15, 5))

        self.lbl_title = ctk.CTkLabel(
            self.title_frame, 
            text="CAD CANVAS", 
            font=Theme.fonts.SUBTITLE, 
            text_color=Theme.TEXT_MAIN.value
        )
        self.lbl_title.pack(side="left")
        tooltip_msg = self.app.lang_manager.get("tooltips.canvas_title", "Winding Layout: Change the phase and direction of the winding for each slot and position to wind the generator.\n\nLeft-click to assign positive polarity, right-click to assign negative polarity. Use number keys to select the active phase.") if self.app else ""
        self.tooltip_title = ToolTip(self.lbl_title, tooltip_msg, small=True)

        self.btn_toggle_guide = ctk.CTkButton(
            self.title_frame,
            text="ⓘ",
            font=Theme.fonts.BODY_BOLD,
            fg_color=Theme.BG_SURFACE.value,
            border_width=1,
            border_color=Theme.BORDER.value,
            hover_color=Theme.BUTTON_HOVER.value,
            text_color=Theme.TEXT_MAIN.value,
            width=30,
            height=30,
            corner_radius=4,
            command=self.toggle_guide
        )
        self.btn_toggle_guide.pack(side="right")

        self.active_phase = 1
        self.guide_visible = False

        # Canvas drawing container
        self.canvas = tk.Canvas(self, bg=Theme.BLUEPRINT_BG.get_color(), highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=15, pady=(5, 5))

        # Overlay frame
        self.overlay_frame = ctk.CTkFrame(self.canvas, fg_color=Theme.BG_SURFACE.value, corner_radius=0)
        self.overlay_textbox = ctk.CTkTextbox(
            self.overlay_frame, 
            wrap="word", 
            fg_color="transparent", 
            text_color=Theme.TEXT_MAIN.value, # type: ignore
            width=650
        )
        self.overlay_textbox.pack(expand=True, fill="y", pady=60)
        
        # Simple Markdown parsing
        # Access internal _textbox to bypass CTkTextbox font scaling restriction
        font_h2 = (Theme.fonts.SUBTITLE[0], Theme.fonts.SUBTITLE[1] + 12, "bold")
        font_body = (Theme.fonts.BODY[0], Theme.fonts.BODY[1] + 6)
        
        self.overlay_textbox._textbox.tag_config("h2", font=font_h2, justify="left", spacing1=35, spacing3=15)
        self.overlay_textbox._textbox.tag_config("body", font=font_body, justify="left", spacing1=0, spacing2=8, spacing3=10)
        self.overlay_textbox._textbox.tag_config("list_item", font=font_body, justify="left", spacing1=4, spacing2=8, spacing3=4, lmargin1=0, lmargin2=22)
        
        self.populate_guide_text()

        # Bind resize event to redraw canvas dynamically
        self.canvas.bind("<Configure>", lambda e: self.update_geometry())
        
        # Mouse interactions
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<B1-Motion>", self.on_drag_left)
        self.canvas.bind("<Button-2>", self.on_right_click)
        self.canvas.bind("<B2-Motion>", self.on_drag_right)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<B3-Motion>", self.on_drag_right)
        
        # Focus canvas on enter so it receives keyboard events
        self.canvas.bind("<Enter>", lambda e: self.canvas.focus_set())
        
        # Keyboard number bindings (0-9)
        for i in range(10):
            self.canvas.bind(str(i), self.on_key_press)

    def toggle_guide(self):
        if self.guide_visible:
            self.overlay_frame.place_forget()
            self.btn_toggle_guide.configure(text="ⓘ")
        else:
            self.overlay_frame.place(relwidth=1, relheight=1)
            self.btn_toggle_guide.configure(text="✕")
        self.guide_visible = not self.guide_visible

    def on_left_click(self, event):
        if hasattr(self, 'legend_rects'):
            for phase, (x0, y0, x1, y1) in self.legend_rects.items():
                if x0 <= event.x <= x1 and y0 <= event.y <= y1:
                    self.active_phase = phase
                    self.update_geometry()
                    return

        self.paint_cell(event.x, event.y, is_right_click=False)

    def on_right_click(self, event):
        self.paint_cell(event.x, event.y, is_right_click=True)

    def on_drag_left(self, event):
        self.paint_cell(event.x, event.y, is_right_click=False)

    def on_drag_right(self, event):
        self.paint_cell(event.x, event.y, is_right_click=True)

    def paint_cell(self, x, y, is_right_click):
        if not hasattr(self, 'grid_start_x'): return
        s = int((x - self.grid_start_x) / self.cell_w)
        p = int((y - self.grid_start_y) / self.cell_h)
        if 0 <= p < self.positions and 0 <= s < self.slots:
            target_val = 0 if self.active_phase == 0 else (-self.active_phase if is_right_click else self.active_phase)
            if self.matrix[p, s] != target_val:
                self.matrix[p, s] = target_val
                self.update_geometry()
                if self.app and hasattr(self.app, 'on_inputs_changed'):
                    self.app.on_inputs_changed()

    def on_key_press(self, event):
        try:
            num = int(event.char)
        except ValueError:
            return
        
        if num > self.phases:
            return  # Ignore keys higher than available phases
            
        self.active_phase = num
        self.update_geometry()

    def update_geometry(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10 or h < 10:
            return

        bg_color = Theme.BLUEPRINT_BG.get_color()
        self.canvas.delete("all")
        self.canvas.configure(bg=bg_color)
        
        # Update frame styling
        self.configure(fg_color=Theme.BG_SURFACE.value, border_color=Theme.BORDER.value)
        
        self.draw_windings_mockup(w, h)

    def draw_windings_mockup(self, w, h):
        if self.app:
            self.matrix = self.app.winding_state.winding_matrix
            self.positions = self.app.winding_state.positions
            self.slots = self.app.winding_state.slots
            self.phases = self.app.winding_state.phases
        else:
            import numpy as np
            self.positions = 4
            self.slots = 38
            self.phases = 5
            self.matrix = np.array([
                [ 1,  1,  1, -3, -3,  2,  2,  2, -1, -1,  3,  3,  3, -2, -2,  1,  1,  1, -3, -3,  5,  5,  2, -1, -1,  3,  3,  3, -5, -2,  3,  3,  4, -2, -2,  1, -4,  1],
                [ 1,  1,  1, -3, -3,  2,  2,  2, -1, -1,  3,  3,  3, -2, -2,  1,  1,  1, -3, -3,  5,  5,  2, -1, -1,  3,  3,  3, -5, -5,  3,  3,  4, -2, -2,  1, -4,  1],
                [ 1,  1, -3, -3, -3,  2,  2, -1, -1, -1,  3,  3, -2, -2, -2,  1,  1, -3, -3, -3,  5,  5, -1, -1, -1,  3,  3, -2, -5, -5,  3,  3,  4, -2, -2,  1, -4, -3],
                [ 1,  1, -3, -3, -3,  2,  2, -1, -1, -1,  3,  3, -2, -2, -2,  1,  1, -3, -3, -3,  5,  5, -1, -1, -1,  3,  3, -2, -5, -5,  3,  3,  4, -2, -2,  1, -4, -3]
            ])

        if self.active_phase > self.phases:
            self.active_phase = self.phases

        text_color = Theme.TEXT_MAIN.get_color()
        
        title_font = ("Arial", int(16 * self.scale_factor), "bold")
        chart_title = self.app.lang_manager.get("canvas.chart_title") if self.app else "Winding Layout"
        self.canvas.create_text(
            w / 2, 25 * self.scale_factor, 
            text=chart_title, 
            fill=text_color, 
            font=title_font
        )

        phase_colors = {
            1: "#EF4444", # Red
            2: "#3B82F6", # Blue
            3: "#10B981", # Green
            4: "#F59E0B", # Yellow
            5: "#8B5CF6", # Purple
            6: "#EC4899", # Pink
            7: "#06B6D4", # Cyan
            8: "#F97316", # Orange
            9: "#84CC16", # Lime
            10: "#6366F1" # Indigo
        }

        margin_x = 40 * self.scale_factor
        margin_y = 70 * self.scale_factor
        available_w = w - 2 * margin_x
        available_h = h - margin_y - 40 * self.scale_factor

        if available_w <= 0 or available_h <= 0:
            return

        cell_w = available_w / self.slots
        cell_h = available_h / self.positions

        cell_h = min(cell_h, 80 * self.scale_factor)
        cell_w = min(cell_w, 40 * self.scale_factor)

        grid_w = cell_w * self.slots
        grid_h = cell_h * self.positions

        start_x = (w - grid_w) / 2
        start_y = 60 * self.scale_factor + (h - 60 * self.scale_factor - grid_h - 30 * self.scale_factor) / 2

        self.grid_start_x = start_x
        self.grid_start_y = start_y
        self.cell_w = cell_w
        self.cell_h = cell_h

        for p in range(self.positions):
            self.canvas.create_text(
                start_x - 15 * self.scale_factor,
                start_y + p * cell_h + cell_h / 2,
                text=f"P{p+1}",
                fill=text_color,
                font=("Arial", int(10 * self.scale_factor), "bold")
            )
            for s in range(self.slots):
                val = self.matrix[p, s]
                
                if p == 0:
                    self.canvas.create_text(
                        start_x + s * cell_w + cell_w / 2,
                        start_y - 10 * self.scale_factor,
                        text=f"{s+1}",
                        fill=text_color,
                        font=("Arial", int(8 * self.scale_factor))
                    )

                x0 = start_x + s * cell_w
                y0 = start_y + p * cell_h
                x1 = x0 + cell_w
                y1 = y0 + cell_h

                if val == 0:
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill="", outline=Theme.BORDER.get_color())
                    continue

                phase = abs(val)
                is_up = val > 0
                
                color = phase_colors.get(phase, "#FFFFFF")

                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=Theme.BORDER.get_color())

                cx = (x0 + x1) / 2
                cy = (y0 + y1) / 2
                arrow_size = min(cell_w, cell_h) * 0.25

                if is_up:
                    self.canvas.create_line(cx, cy + arrow_size, cx, cy - arrow_size, arrow="last", fill="white", width=2 * self.scale_factor)
                else:
                    self.canvas.create_line(cx, cy - arrow_size, cx, cy + arrow_size, arrow="last", fill="white", width=2 * self.scale_factor)

        legend_start_y = start_y + grid_h + 30 * self.scale_factor
        legend_item_width = 85 * self.scale_factor
        
        total_legend_items = self.phases + 1
        legend_start_x = (w - (legend_item_width * total_legend_items)) / 2

        self.legend_rects = {}

        for i in range(0, self.phases + 1):
            lx = legend_start_x + i * legend_item_width
            ly = legend_start_y
            box_size = 20 * self.scale_factor
            
            self.legend_rects[i] = (lx, ly, lx + legend_item_width, ly + box_size)
            
            if i == 0:
                color = Theme.BG_SURFACE.get_color()
                label = self.app.lang_manager.get("canvas.legend_empty") if self.app else "Empty"
            else:
                color = phase_colors.get(i, "#FFFFFF")
                phase_fmt = self.app.lang_manager.get("canvas.legend_phase") if self.app else "Phase {phase}"
                label = phase_fmt.format(phase=i)
                
            outline_color = Theme.ACCENT.get_color() if i == self.active_phase else Theme.BORDER.get_color()
            outline_width = 3 * self.scale_factor if i == self.active_phase else 1 * self.scale_factor
            
            self.canvas.create_rectangle(lx, ly, lx + box_size, ly + box_size, fill=color, outline=outline_color, width=outline_width)
            
            text_weight = "bold" if i == self.active_phase else "normal"
            self.canvas.create_text(lx + box_size + 10 * self.scale_factor, ly + box_size / 2, text=label, fill=text_color, font=("Arial", int(10 * self.scale_factor), text_weight), anchor="w")

    def update_language(self):
        if not self.app:
            return
        self.lbl_title.configure(text=self.app.lang_manager.get("canvas.title"))
        if hasattr(self, 'tooltip_title'):
            tooltip_msg = self.app.lang_manager.get("tooltips.canvas_title", "Winding Layout: Change the phase and direction of the winding for each slot and position to wind the generator.\n\nLeft-click to assign positive polarity, right-click to assign negative polarity. Use number keys to select the active phase.")
            self.tooltip_title.update_text(tooltip_msg)
        if hasattr(self, 'overlay_textbox'):
            self.populate_guide_text()
        self.update_geometry()

    def populate_guide_text(self):
        self.overlay_textbox.configure(state="normal")
        self.overlay_textbox.delete("1.0", "end")
        
        if self.app:
            guide_text = self.app.lang_manager.get("canvas.guide_text", "")
            # Fallback to English hardcoded text if key is missing/untranslated
            if guide_text.startswith("[") and guide_text.endswith("]"):
                from .content import WINDING_GUIDE_TEXT
                guide_text = WINDING_GUIDE_TEXT
        else:
            from .content import WINDING_GUIDE_TEXT
            guide_text = WINDING_GUIDE_TEXT
            
        for line in guide_text.split('\n'):
            if line.startswith('## '):
                self.overlay_textbox.insert("end", line[3:] + "\n", "h2")
            elif line.startswith('• ') or (len(line) > 2 and line[0].isdigit() and line[1:3] == '. '):
                self.overlay_textbox.insert("end", line + "\n", "list_item")
            else:
                self.overlay_textbox.insert("end", line + "\n", "body")
                
        self.overlay_textbox.configure(state="disabled")