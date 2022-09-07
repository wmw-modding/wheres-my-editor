from importlib.resources import path
import threading
import tkinter as tk
from tkinter import StringVar, ttk

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
    
class settings_dialog():
    def __init__(self, root, settings: dict, page=0) -> None:
        self.window = tk.Toplevel()
        self.settings = settings
        self.page = page

        self.window.geometry('500x400')

        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True)
        self.tabs = {}
        self.load_tabs()

        for tab in self.tabs:
            print('adding: ', tab)
            self.notebook.add(self.tabs[tab], text=tab)

        self.window.transient(root)
        self.window.wait_window()

    def load_tabs(self):
        self.tabs['Paths'] = self.paths()

    def paths(self):
        def gamedir():
            def update_game_dir(game, path):
                games = {
                    'wmw' : game_paths['wmw']
                }

                games['wmw']

            label_frame = ttk.LabelFrame(frame, text='Game paths')
            vars = {
                'wmw' : tk.StringVar()
            }
            game_paths = {
                'wmw' : {
                    "label" : ttk.Label(label_frame, text="Where's My Water?"),
                    "entry" : ttk.Entry(label_frame, width=50, textvariable=vars['wmw']),
                    "button" : ttk.Button(label_frame, text='browse')
                }
            }

            label_frame.pack(anchor='w', fill='x')

            label_frame.columnconfigure(0, minsize=120)
            label_frame.columnconfigure(1, weight=1)

            game_paths['wmw']['label'].grid(column=0, row=0, sticky='e', padx=10)
            game_paths['wmw']['entry'].grid(column=1, row=0, sticky='e')
            game_paths['wmw']['button'].grid(column=2, row=0, sticky='w', padx=5)

        def defualt_paths():
            label_frame = ttk.LabelFrame(frame, text='Defualt level')

            vars = {
                "png" : tk.StringVar(),
                "xml" : tk.StringVar()
            }
            paths = {
                "png" : {
                    "label" : ttk.Label(label_frame, text='Image'),
                    "entry" : ttk.Entry(label_frame, width=50, textvariable=vars['png']),
                    "button" : ttk.Button(label_frame, text='browse')
                },
                "xml" : {
                    "label" : ttk.Label(label_frame, text='XML'),
                    "entry" : ttk.Entry(label_frame, width=50, textvariable=vars['xml']),
                    "button" : ttk.Button(label_frame, text='browse')
                }
            }

            label_frame.pack(anchor='w', fill='x')
            label_frame.columnconfigure(0, minsize=120)
            label_frame.columnconfigure(1, weight=1)

            paths['png']['label'].grid(column=0, row=0, sticky='e', padx=10)
            paths['png']['entry'].grid(column=1, row=0, sticky='e')
            paths['png']['button'].grid(column=2, row=0, sticky='w', padx=5)

            paths['xml']['label'].grid(column=0, row=1, sticky='e', padx=10)
            paths['xml']['entry'].grid(column=1, row=1, sticky='e')
            paths['xml']['button'].grid(column=2, row=1, sticky='w', padx=5)

        frame = ttk.Frame(self.notebook)
        # frame.grid()
        frame.pack(fill='both', expand=True)

        gamedir()
        defualt_paths()

        return frame
