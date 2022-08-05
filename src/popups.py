import threading
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
    def __init__(self, root=None, max=280) -> None:
        # super().__init__()
        # threading.Thread.__init__(self)
        self.window = tk.Toplevel()
        self.window.wm_title('loading...')
        self.window.grid()
        self.bar = ttk.Progressbar(
            self.window,
            orient='horizontal',
            mode='determinate',
            length=280
        )

        self.window.transient(root)

        self.bar['max'] = max

        self.bar.grid(column=0, row=0, columnspan=2, padx=10, pady=20)

        # self.window.wait_window()

        # self.bar.start()

    def init(self):
        pass

    def run(self, command=None, args=()):
        if not command:
            command(args)

    def addProgress(self, value):
        self.bar['value'] += value

    def close(self):
        self.window.destroy()
    