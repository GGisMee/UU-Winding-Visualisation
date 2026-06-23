import customtkinter as ctk

app = ctk.CTk()
var = ctk.DoubleVar(value=5)

def on_change(val):
    print("on_change called with:", val)

slider = ctk.CTkSlider(app, variable=var, command=on_change)
slider.pack()

def update_var():
    print("Updating var...")
    var.set(10)
    print("Var updated!")

def update_slider_state():
    print("Updating state...")
    slider.configure(state="disabled")
    slider.configure(state="normal")
    print("State updated!")

app.after(500, update_var)
app.after(1000, update_slider_state)
app.after(1500, app.destroy)

app.mainloop()
