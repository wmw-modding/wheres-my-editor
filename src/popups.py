import tkinter as tk
from tkinter import ttk

def commingsoon():
    popup = tk.Toplevel()
    popup.wm_title('.')
    ttk.Label(popup, text="Comming Soon maybe").pack()
    ttk.Button(popup, text="OK", command = popup.destroy ).pack()
       

def about_dialog():
    popup = tk.Toplevel()
    popup.wm_title('About')
    ttk.Label(popup, text="Hai").pack()
    ttk.Label(popup, text="Enjoying the program?").pack()
    ttk.Button(popup, text="Eh", command = popup.destroy ).pack()

class load_dialog():
    def __init__(self) -> None:
        self.window = tk.Toplevel()
        self.window.wm_title('loading...')
        self.window.grid()
        pb = ttk.Progressbar(
            self.window,
            orient='horizontal',
            mode='indeterminate',
            length=280
        )

        pb.grid(column=0, row=0, columnspan=2, padx=10, pady=20)

        pb.start()
    