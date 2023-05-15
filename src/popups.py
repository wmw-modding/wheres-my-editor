import copy
import json
import tkinter as tk
from tkinter import ttk, filedialog
import tkinter.font as tkFont
import os
from PIL import Image, ImageTk
import webbrowser
import numpy
import typing

from scrollframe import ScrollFrame

class About(tk.Toplevel):
    def __init__(
        self,
        parent,
        title = 'About',
        author = 'ego-lay-atman-bay',
        program = "Where's My Editor?",
        version = 'v2.0.0',
        description = '',
        credits : list[dict[typing.Literal['name','url','description'], str]] = [],
        logo : Image.Image = None
    ) -> None:
        super().__init__(parent)
        
        self.style = ttk.Style()
        
        self.style.configure('Hyperlink.TLabel', foreground = "blue")
        
        
        self.heading_font = tkFont.nametofont('TkHeadingFont')
        self.heading_font.configure(size = 20)
        
        self.style.configure('Heading.TLabel', font = self.heading_font)
        
        self.minsize(350,300)
        
        self.title = title
        self.author = author
        self.program = program
        self.version = version
        self.description = description
        self.credits = credits
        self.logo = logo
        
        self.geometry('500x400')
        
        self.addLogo()
        
        self.scrollframe = ScrollFrame(self, usettk=True, height = 100)
        self.frame = self.scrollframe.viewPort
        self.scrollframe.pack(expand=True, fill='both', pady=4)
        
        self.addProgramText()
        self.addDescription()
        self.addCredits()
        
        self.close = ttk.Button(self, text = 'Close', command = self.destroy)
        self.close.pack(anchor = 'n', pady = 2)
        
        self.transient(self.master)
        self.wait_window()
    
    def addLogo(self):
        if self.logo == None:
            return
        elif isinstance(self.logo, str):
            self.logo = Image.open(self.logo)
        elif not isinstance(self.logo, Image.Image):
            return
        
        self.logo = self.resizeImage(self.logo, height = 150)
        
        self.logo_PhotoImage = ImageTk.PhotoImage(self.logo)
        
        self.logo_image = ttk.Label(self, image = self.logo_PhotoImage)
        self.logo_image.pack(side = 'top', anchor = 'n')
    
    def resizeImage(self, image : Image.Image, scale : float = None, width : int = None, height : int = None):
        size = numpy.array(image.size)
        if scale != None:
            size = size / scale
        elif width != None:
            if height == None:
                size[1] *= (width / size[0])
                
            size[0] = width
        elif height != None:
            if width == None:
                size[0] *= (height / size[1])
                
            size[1] = height
        
        return image.resize(tuple(size), resample = Image.Resampling.BILINEAR)
    
    def addProgramText(self):
        self.program_label = ttk.Label(self.frame, text = self.program)
        self.program_label.pack(anchor = 'n')
        
        self.version_label = ttk.Label(self.frame, text = self.version)
        self.version_label.pack(anchor = 'n')
        
        self.author_label = ttk.Label(self.frame, text = f'Created by: {self.author}')
        self.author_label.pack(anchor = 'n')
        
    def addDescription(self):
        self.description_label = tk.Message(self.frame, text = self.description, width=200)
        self.description_label.pack(anchor='n', pady=10)
    
    def addCredits(self):
        self.credits_heading = ttk.Label(self.frame, text='Credits:', style='Heading.TLabel', )
        self.credits_heading.pack()
        
        self.credits_frame = ttk.Frame(self.frame)
        self.credits_frame.pack(anchor = 'n', pady=4)
        
        def addCredit(credit : dict[typing.Literal['name','url','description'], str], row = 0):
            # credit_frame = ttk.Frame(self.credits_frame)
            # credit_frame.pack(anchor='w', expand=True)
            
            if credit['url'] in ['', None]:
                url = ttk.Label(self.credits_frame, text = credit['name'])
            else:
                url = ttk.Label(self.credits_frame, text = credit['name'], style = 'Hyperlink.TLabel', cursor = 'hand2')
                url.bind('<Button-1>', lambda e, link = credit['url']: webbrowser.open(link))
            
            url.grid(column=0, row = row, sticky = 'nw')
            
            description = tk.Message(self.credits_frame, text = credit['description'], width=200)
            description.grid(column=1, row = row, sticky = 'nw',)
        
        row = 0
        
        for credit in self.credits:
            row += 1
            addCredit(credit, row=row)

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

    __version__ = '2.0.0'
    __author__ = 'ego-lay-atman-bay'
    __credits__ = [
        {
            'name' : 'wmwpy',
            'url' : 'https://github.com/wmw-modding/wmwpy',
            'description' : "Where's My Editor? uses wmwpy to read and modify Where's My Water? data, e.g. levels."
        },
        {
            'name' : 'rubice!',
            'url' : 'https://www.youtube.com/channel/UCsY-c5mJYWnK6PhrkHqPwig',
            'description' : 'Thanks to @rubice for creating the logo.'
        },
        {
            'name' : 'campbellsonic',
            'url' : 'https://github.com/campbellsonic',
            'description' : 'Thanks to @campbellsonic for helping to read waltex images.'
        }
    ]


    app = tk.Tk()
    about = About(
        app,
        title = "About",
        author = __author__,
        program = "Where's My Editor?",
        version = __version__,
        description = """Where's My Editor? is a level editor for the Where's My Water? game series.""",
        credits = __credits__,
        logo = Image.open('assets/images/WME_logo.png'),
    )
    
    app.mainloop()