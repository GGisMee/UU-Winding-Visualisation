import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

root = tk.Tk()
root.geometry("400x400")

class StrictRatioPlot(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="red")
        
        self.fig = plt.Figure(figsize=(3, 2), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.plot([0, 1], [0, 1])
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.plot_widget = self.canvas.get_tk_widget()
        self.plot_widget.place(relx=0.5, rely=0.5, anchor="center")
        
        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        # Only care about width changes from the packer
        w = event.width
        
        target_w = w
        target_h = int(target_w * (2.0 / 3.0))
        max_h = 150
        
        if target_h > max_h:
            target_h = max_h
            target_w = int(target_h * (3.0 / 2.0))
            
        current_w = self.plot_widget.winfo_width()
        current_h = self.plot_widget.winfo_height()
        
        if abs(current_w - target_w) > 2 or abs(current_h - target_h) > 2:
            self.plot_widget.configure(width=target_w, height=target_h)
            
        if abs(self.winfo_height() - target_h) > 2:
            self.configure(height=target_h)

plot = StrictRatioPlot(root)
plot.pack(fill="x", padx=20, pady=20)

root.update()
print("Initial Frame:", plot.winfo_width(), plot.winfo_height())
print("Initial Plot:", plot.plot_widget.winfo_width(), plot.plot_widget.winfo_height())

root.geometry("600x400")
root.update()
print("Wider Frame:", plot.winfo_width(), plot.winfo_height())
print("Wider Plot:", plot.plot_widget.winfo_width(), plot.plot_widget.winfo_height())

root.geometry("200x400")
root.update()
print("Narrower Frame:", plot.winfo_width(), plot.winfo_height())
print("Narrower Plot:", plot.plot_widget.winfo_width(), plot.plot_widget.winfo_height())
