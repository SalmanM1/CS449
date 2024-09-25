import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("GUI using Tkinter")
root.geometry("400x300")

label = tk.Label(root, text="Welcome to my Project GUI!")
label.pack(pady=10)

check_var = tk.IntVar()
check_button = tk.Checkbutton(root, text="Enable SOS Game Mode", variable=check_var)
check_button.pack(pady=5)

game_mode = tk.StringVar(value="Simple")

radio_button1 = tk.Radiobutton(root, text="Simple Game", variable=game_mode, value="Simple")
radio_button2 = tk.Radiobutton(root, text="General Game", variable=game_mode, value="General")

radio_button1.pack(pady=5)
radio_button2.pack(pady=5)

def show_selection():
    mode = game_mode.get()
    check_status = "Enabled" if check_var.get() == 1 else "Disabled"
    result_label.config(text=f"Game Mode: {mode}, SOS Mode: {check_status}")

submit_button = ttk.Button(root, text="Submit", command=show_selection)
submit_button.pack(pady=10)

result_label = tk.Label(root, text="")
result_label.pack(pady=10)

root.mainloop()