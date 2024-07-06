import logging
import copy
import json
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
import tkinter.font as tkFont
import os
import pathlib
from PIL import Image, ImageTk
import webbrowser
import numpy
import typing
import wmwpy

from scrollframe import ScrollFrame
from settings import Settings

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
        
        
        self.heading_font = tkFont.nametofont('TkHeadingFont').copy()
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
        
        self.version_label = ttk.Label(self.frame, text = self.version, justify = 'center')
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
    
class SettingsDialog(tk.Toplevel):
    def __init__(self, root, settings: Settings, page=0) -> None:
        super().__init__(root)
        
        self._settings = copy.deepcopy(settings)
        self.settings = settings
        self.page = page

        self.geometry('500x400')

        self.notebook = ttk.Notebook(self)
        self.tabs = {}
        self.load_tabs()
        self.notebook.pack(fill='both', expand=True)
            
        self.confirm = {
            'frame': ttk.Frame(self)
        }
        
        self.confirm['ok'] = ttk.Button(self.confirm['frame'], text='Ok', command=lambda : self.close(True))
        self.confirm['cancel'] = ttk.Button(self.confirm['frame'], text='Cancel', command=lambda : self.close(False))
        
        self.confirm['ok'].pack(side='right', padx=2, pady=2)
        self.confirm['cancel'].pack(side='right', padx=2, pady=2)
        
        self.confirm['notice'] = ttk.Label(self.confirm['frame'], text = 'Changes will apply at next launch')
        self.confirm['notice'].pack(side='left', padx=2)
        
        self.confirm['frame'].pack(anchor='s', fill='x')
        
        self.protocol("WM_DELETE_WINDOW", lambda *args : self.close(False))

        self.transient(root)
        self.wait_window()
        
    def close(self, saveSettings = True):
        # print(self.settings)
        # print(self._settings)
        if not saveSettings:
            self.settings.update(self._settings)
            self.settings.save()
        
        self.destroy()

    def load_tabs(self):
        # self.paths()
        self.createPaths()
        
    def createPaths(self):
        def create_row(
            parent : tk.Widget = self,
            label_text : str = '',
            entry_type : typing.Literal['text', 'options'] = 'text',
            entry_callback : typing.Callable[[str], str] = None,
            default_value : str = '',
            use_button : bool = True,
            button_text : str = 'Browse',
            button_callback : typing.Callable[[str], typing.Any] = None,
            row = 0,
            options : list[str] = []
        ) -> dict[typing.Literal[
            'label',
            'var',
            'entry',
            'button',
        ]]:
            
            label = ttk.Label(
                parent,
                text = label_text,
            )
            label.grid(row = row, column = 0, sticky='ew', padx=4, pady=2)
            
            var = tk.StringVar(
                value = default_value,
            )
            var.trace(
                'w',
                lambda *args : entry_callback(var.get()),
            )
            
            def get_entry(
                type : typing.Literal['text', 'options'],
                var,
                options : list = [],
            ):
                if type == 'options':
                    return ttk.Combobox(
                        parent,
                        textvariable = var,
                        values = options,
                    )
                else:
                    return ttk.Entry(
                        parent,
                        textvariable = var,
                    )
            
            entry = get_entry(
                entry_type,
                var = var,
                options = options,
            )
            # entry.insert(0, var.get())
            entry.grid(row = row, column = 1, sticky = 'ew', padx=4, pady=2)
            
            button = None
            
            if use_button:
                button = ttk.Button(
                    parent,
                    text = button_text,
                    command = lambda *args : var.set(button_callback(var.get())),
                )
                button.grid(row = row, column = 2, sticky = 'ew', padx=4, pady=2)
            
            return {
                'label' : label,
                'var' : var,
                'entry' : entry,
                'button' : button,
            }
        
        def validate(
            default = '',
            result = None,
        ):
            if result in ['', None]:
                return default
            else:
                return result
            
        self.paths : dict[typing.Literal['frame', 'contents'], ttk.Frame | dict[typing.Literal['frame', 'contents'], dict[str, tk.Widget]]] = {
            'frame': ttk.Frame(self.notebook),
            'contents': {
                'game': {
                    'contents': {}
                },
                'level': {
                    'contents': {}
                }
            }
        }
        
        self.notebook.add(self.paths['frame'], text='Paths', sticky='nsew')
        
        # game
        self.paths['contents']['game']['frame'] = ttk.LabelFrame(self.paths['frame'], text='Game')
        self.paths['contents']['game']['frame'].pack(fill='x', anchor='n', side='top')
        self.paths['contents']['game']['frame'].columnconfigure(1, weight=1)
        
        self.paths['contents']['game']['contents']['gamepath'] = create_row(
            self.paths['contents']['game']['frame'],
            label_text = 'Game path',
            entry_type = 'text',
            entry_callback = lambda value : self.settings.set('game.gamepath', value),
            default_value = self.settings.get('game.gamepath'),
            button_callback = lambda path : validate(
                path,
                filedialog.askdirectory(
                    initialdir = os.path.dirname(path),
                    title = 'Game directory',
                )
            ),
            row = 0,
        )
        self.paths['contents']['game']['contents']['assets'] = create_row(
            self.paths['contents']['game']['frame'],
            label_text = 'Assets path',
            entry_type = 'text',
            entry_callback = lambda value : self.settings.set('game.assets', value),
            default_value = self.settings.get('game.assets'),
            button_callback = lambda path : os.path.relpath(
                validate(
                    wmwpy.utils.path.joinPath(self.settings.get('game.gamepath'), path),
                    filedialog.askdirectory(
                        initialdir = os.path.dirname(wmwpy.utils.path.joinPath(self.settings.get('game.gamepath'), path)),
                        title = 'Assets directory',
                    )
                ),
                self.settings.get('game.gamepath')
            ),
            row = 1,
        )
        self.paths['contents']['game']['contents']['game'] = create_row(
            self.paths['contents']['game']['frame'],
            label_text = 'Game',
            entry_type = 'options',
            options = list(wmwpy.GAMES.keys()),
            entry_callback = lambda value : self.settings.set('game.game', value),
            default_value = self.settings.get('game.game'),
            use_button = False,
            row = 2,
        )
        
        # default level
        def getFile(path : str):
            logging.debug(f'getFile: path: {path}')
            if not isinstance(path, str):
                raise TypeError('path must be str')
            
            if path in ['', None]:
                logging.debug('getFile: no path')
                return ''
            
            if path.startswith(':game:'):
                logging.debug(f'getFile: path starts with :game:')
                path = path.partition(':game:')[-1]
                
                path = pathlib.Path('/', path).as_posix()
                
                logging.debug(f'getFile: path after :game: {path}')
                
                return file
            
            path = pathlib.PurePath(path)
            assets = os.path.abspath(wmwpy.utils.path.joinPath(
                self.settings.get('game.gamepath'),
                self.settings.get('game.assets'),
            ))
            
            print(f'getFile: In filesystem? {path.is_relative_to(assets)}')
            if path.is_relative_to(assets):
                logging.debug(f'getFile: relative path')
                relPath = os.path.relpath(path, assets)
                relPath = pathlib.Path('/', relPath).as_posix()
                logging.debug(f'getFile: rel path: {relPath}')
                file = f':game:{relPath}'
                
                logging.debug(f'getFile: file: {file}')
                return file
            
            if path in ['', None]:
                logging.debug('getFile: no path')
                return ''
            else:
                logging.debug(f'getFile: absolute path: {path}')
                file = path
            
            return file
        
        self.paths['contents']['level']['frame'] = ttk.LabelFrame(self.paths['frame'], text='Default level')
        self.paths['contents']['level']['frame'].pack(fill='x', anchor='n', side='top')
        self.paths['contents']['level']['frame'].columnconfigure(1, weight=1)
        
        self.paths['contents']['level']['contents']['xml'] = create_row(
            self.paths['contents']['level']['frame'],
            label_text = 'XML',
            entry_type = 'text',
            entry_callback = lambda value : self.settings.set('game.default_level.xml', value),
            default_value = self.settings.get('game.default_level.xml'),
            button_callback = lambda path : 
                validate(
                    path,
                    getFile(
                        filedialog.askopenfilename(
                            defaultextension = '.xml',
                            filetypes = (
                                (f'{self.settings.get("game.game")} Level', '*.xml'),
                                ('Any', '*.*')
                            ),
                            initialdir = wmwpy.utils.joinPath(
                                self.settings.get('game.gamepath'),
                                self.settings.get('game.assets'),
                            ),
                            title = 'Pick default XML file',
                        )
                    )
                ),
            row = 0,
        )
        self.paths['contents']['level']['contents']['image'] = create_row(
            self.paths['contents']['level']['frame'],
            label_text = 'Image',
            entry_type = 'text',
            entry_callback = lambda value : self.settings.set('game.default_level.image', value),
            default_value = self.settings.get('game.default_level.image'),
            button_callback = lambda path : 
                validate(
                    path,
                    getFile(
                        filedialog.askopenfilename(
                            defaultextension = '.png',
                            filetypes = (
                                (f'{self.settings.get("game.game")} Level', '*.png'),
                                ('Any', '*.*')
                            ),
                            initialdir = wmwpy.utils.joinPath(
                                self.settings.get('game.gamepath'),
                                self.settings.get('game.assets'),
                            ),
                            title = 'Pick defualt PNG file',
                        )
                    )
                ),
            row = 1,
        )
        
    def updateSettings(self):
        self.settings.set('game.gamepath', self.paths['contents']['gamepaths']['var'].get())
        self.settings.set('game.default_level.image', self.paths['contents']['level']['image']['var'].get())
        self.settings.set('game.default_level.xml', self.paths['contents']['level']['xml']['var'].get())

class _AskStringOptions(simpledialog.Dialog):
    def __init__(
        self,
        parent: tk.Misc | None,
        title: str | None = None,
        prompt : str = None,
        validate_message :  str = None,
        options : list[str] = [],
        validate_callback : typing.Callable[[str], bool] = None,
    ) -> None:
        self.options = copy.deepcopy(options)
        self.validate_callback = validate_callback
        self.prompt = prompt
        self.validate_message = validate_message
        
        super().__init__(parent, title)
    
    def body(self, master: tk.Frame) -> tk.Misc | None:
        if isinstance(self.prompt, str):
            prompt = ttk.Label(
                master,
                text = self.prompt,
            )
            
            prompt.pack(side = 'top', anchor = 'center')
        
        if len(self.options) > 0:
            self.entry = ttk.Combobox(
                master,
                values = self.options,
            )
        else:
            self.entry = ttk.Entry(
                master
            )
        
        self.entry.pack(fill = 'x')
        
        self.style = ttk.Style(self)
        self.style.configure('Validation.TLabel', foreground = "red")
        
        self.validate_label = ttk.Label(
            master,
            text = self.validate_message if isinstance(self.validate_message, str) else 'Error',
            style = 'Validation.TLabel',
            anchor = 'nw',
        )
        
        return self.entry
    
    def buttonbox(self) -> None:
        box = ttk.Frame(self)

        w = ttk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()
    
    def apply(self) -> None:
        return self.entry.get()
    
    def validate(self) -> bool:
        self.result = self.entry.get()
        
        if callable(self.validate_callback):
            validation = self.validate_callback(self.result)
        else:
            validation = True
        
        if not validation:
            self.validate_label.pack(anchor = 'ne', side = 'left')
        
        return validation

def askstringoptions(
    parent = None,
    title = None,
    prompt : str = None,
    validate_message : str = None,
    options : list[str] = [],
    validate_callback : typing.Callable[[str], bool] = None,
    **kwargs
):
    d = _AskStringOptions(
        parent = parent,
        title = title,
        prompt = prompt,
        validate_message = validate_message,
        options = options,
        validate_callback = validate_callback,
        **kwargs
    )
    
    return d.result


if __name__ == '__main__':
    test = 'settings'

    if test == 'about':
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

    elif test == 'settings':
        settings = Settings('settings.json')
        
        app = tk.Tk()
        dialog = SettingsDialog(
            app,
            settings = settings
        )
