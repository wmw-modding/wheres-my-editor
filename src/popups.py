import copy
import json
import tkinter as tk
from tkinter import StringVar, ttk, filedialog
import os

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
        self._settings = copy.deepcopy(settings)
        self.settings = copy.deepcopy(settings)
        self.page = page

        self.window.geometry('500x400')

        self.notebook = ttk.Notebook(self.window)
        self.tabs = {}
        self.load_tabs()
        self.notebook.pack(fill='both', expand=True)
            
        self.confirm = {
            'frame': ttk.Frame(self.window)
        }
        
        self.confirm['ok'] = ttk.Button(self.confirm['frame'], text='Ok', command=lambda : self.close(True))
        self.confirm['cancel'] = ttk.Button(self.confirm['frame'], text='Cancel', command=lambda : self.close(False))
        
        self.confirm['ok'].pack(side='right', padx=2, pady=2)
        self.confirm['cancel'].pack(side='right', padx=2, pady=2)
        
        self.confirm['frame'].pack(anchor='s', fill='x')

        self.window.transient(root)
        self.window.wait_window()
        
    def close(self, saveSettings = True):
        print(self.settings)
        print(self._settings)
        if not saveSettings:
            self.settings = self._settings
        
        self.window.destroy()

    def load_tabs(self):
        # self.paths()
        self.createPaths()
        
    def createPaths(self):
        def browse(entry, type='file', **kwargs):
            path = ''
            print(kwargs)

            if type in ['dir', 'directory']:
                path = filedialog.askdirectory(**kwargs)
            else:
                path = filedialog.askopenfilename(**kwargs)

            if path in ['', None]:
                return
            entry.delete(0, 'end')
            entry.insert(0, path)
            
        self.paths = {
            'frame': ttk.Frame(self.notebook),
            'contents': {
                'gamepaths': {
                    'wmw': {
                        'var': tk.StringVar(value=self.settings['gamedir'])
                    }
                },
                'level': {
                    'image': {
                        'var': tk.StringVar(value=self.settings['default_level']['image'])
                    },
                    'xml': {
                        'var': tk.StringVar(value=self.settings['default_level']['xml'])
                    }
                }
            }
        }
        
        self.paths['contents']['gamepaths']['frame'] = ttk.LabelFrame(self.paths['frame'], text='Game paths')
        # self.paths['contents']['gamepaths']['wmw']['frame'] = ttk.Frame(self.paths['contents']['gamepaths']['frame'])
        self.paths['contents']['gamepaths']['wmw']['label'] = ttk.Label(self.paths['contents']['gamepaths']['frame'], text="Where's My Water?")
        self.paths['contents']['gamepaths']['wmw']['entry'] = ttk.Entry(self.paths['contents']['gamepaths']['frame'], textvariable=self.paths['contents']['gamepaths']['wmw']['var'])
        self.paths['contents']['gamepaths']['wmw']['button'] = ttk.Button(self.paths['contents']['gamepaths']['frame'], text='Browse', command=lambda : browse(
            self.paths['contents']['gamepaths']['wmw']['entry'],
            'dir',
            title='Choose game directory',
            initialdir = self.paths['contents']['gamepaths']['wmw']['var'].get()
            )
        )
        
        self.paths['contents']['level']['frame'] = ttk.LabelFrame(self.paths['frame'], text='Default level')
        # self.paths['contents']['gamepaths']['image']['frame'] = ttk.Frame(self.paths['contents']['level']['frame'])
        self.paths['contents']['level']['image']['label'] = ttk.Label(self.paths['contents']['level']['frame'], text="Image")
        self.paths['contents']['level']['image']['entry'] = ttk.Entry(self.paths['contents']['level']['frame'], textvariable=self.paths['contents']['level']['image']['var'])
        self.paths['contents']['level']['image']['button'] = ttk.Button(
            self.paths['contents']['level']['frame'],
            text='Browse', command=lambda : browse(
                self.paths['contents']['level']['image']['entry'],
                'file', title = 'Choose level image', defaultextension='*.png' ,
                filetypes = (
                    (
                        ('wmw level image', '*.png'),
                        ('any', '*.*')
                    )
                ),
                initialdir = os.path.dirname(self.paths['contents']['level']['image']['var'].get())
            )
        )
        
        
        self.paths['contents']['level']['xml']['label'] = ttk.Label(self.paths['contents']['level']['frame'], text="XML")
        self.paths['contents']['level']['xml']['entry'] = ttk.Entry(self.paths['contents']['level']['frame'], textvariable=self.paths['contents']['level']['xml']['var'])
        self.paths['contents']['level']['xml']['button'] = ttk.Button(
            self.paths['contents']['level']['frame'],
            text='Browse', command=lambda : browse(
                self.paths['contents']['level']['xml']['entry'],
                'file', title='Choose level XML', defaultextension='*.xml' ,
                filetypes = (
                    (
                        ('wmw level XML', '*.xml'),
                        ('any', '*.*')
                    )
                ),
                initialdir = os.path.dirname(self.paths['contents']['level']['xml']['var'].get())
            )
        )
        
        self.paths['contents']['gamepaths']['wmw']['label'].grid(row=0, column=0, sticky='e', padx=2, pady=2)
        self.paths['contents']['gamepaths']['wmw']['entry'].grid(row=0, column=1, sticky='ew', padx=2, pady=2)
        self.paths['contents']['gamepaths']['wmw']['button'].grid(row=0, column=2, padx=2, pady=2)
        
        self.paths['contents']['gamepaths']['wmw']['var'].trace('w', lambda name, index, mode: self.updateSettings())

        self.paths['contents']['level']['image']['label'].grid(row=0, column=0, sticky='e', padx=2, pady=2)
        self.paths['contents']['level']['image']['entry'].grid(row=0, column=1, sticky='ew', padx=2, pady=2)
        self.paths['contents']['level']['image']['button'].grid(row=0, column=2, padx=2, pady=2)
        
        self.paths['contents']['level']['image']['var'].trace('w', lambda name, index, mode: self.updateSettings())

        self.paths['contents']['level']['xml']['label'].grid(row=1, column=0, sticky='e', padx=2, pady=2)
        self.paths['contents']['level']['xml']['entry'].grid(row=1, column=1, sticky='ew', padx=2, pady=2)
        self.paths['contents']['level']['xml']['button'].grid(row=1, column=2, padx=2, pady=2)
        
        self.paths['contents']['level']['xml']['var'].trace('w', lambda name, index, mode: self.updateSettings())

        # self.paths['contents']['gamepaths']['frame'].columnconfigure(0, weight=1)
        # self.paths['contents']['level']['frame'].columnconfigure(0, weight=1)
        self.paths['contents']['gamepaths']['frame'].columnconfigure(1, weight=1)
        self.paths['contents']['level']['frame'].columnconfigure(1, weight=1)

        self.paths['contents']['gamepaths']['frame'].pack(fill='x', anchor='n', side='top')
        self.paths['contents']['level']['frame'].pack(fill='x', anchor='n', side='top')
        
        self.notebook.add(self.paths['frame'], text='Paths', sticky='nsew')
        
    def updateSettings(self):
        self.settings['gamedir'] = self.paths['contents']['gamepaths']['wmw']['var'].get()
        self.settings['default_level']['image'] = self.paths['contents']['level']['image']['var'].get()
        self.settings['default_level']['xml'] = self.paths['contents']['level']['xml']['var'].get()

if __name__ == '__main__':
    with open('settings.json') as file:
        settings = json.load(file)

    app = tk.Tk()
    settings_dialog(app, settings)