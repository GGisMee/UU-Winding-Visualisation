import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

root = tk.Tk()
root.geometry("400x400")

fig = plt.Figure(figsize=(3, 2), dpi=100)
ax = fig.add_subplot(111)
ax.plot([0, 1], [0, 1])

canvas = FigureCanvasTkAgg(fig, master=root)
widget = canvas.get_tk_widget()
widget.pack(fill="x", padx=20, pady=20)

def on_resize(event):
    w = event.width
    target_h = int(w / 2.0)
    max_h = 150
    if target_h > max_h:
        target_h = max_h
        
    current_h = widget.winfo_height()
    if abs(current_h - target_h) > 2:
        widget.configure(height=target_h)

widget.bind("<Configure>", on_resize, add="+")

root.update()
print("Initial:", widget.winfo_width(), widget.winfo_height())
root.geometry("600x400")
root.update()
print("After wider:", widget.winfo_width(), widget.winfo_height())
root.geometry("200x400")
root.update()
print("After narrower:", widget.winfo_width(), widget.winfo_height())
