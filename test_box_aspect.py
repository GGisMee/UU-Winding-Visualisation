import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

root = tk.Tk()
root.geometry("600x400")

fig = plt.Figure(figsize=(3, 2), dpi=100)
ax = fig.add_subplot(111)
ax.plot(np.linspace(0, 2*np.pi, 100), np.sin(np.linspace(0, 2*np.pi, 100)))
ax.set_xlim(0, 2*np.pi)
ax.set_ylim(-1.2, 1.2)
ax.set_box_aspect(2/3)  # THIS IS THE MAGIC BULLET! height is 2/3 of width

canvas = FigureCanvasTkAgg(fig, master=root)
widget = canvas.get_tk_widget()
widget.pack(fill="x", padx=20, pady=20)

root.update()
fig.savefig("test_box_aspect.png")
print("Done. Saved image.")
