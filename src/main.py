__version__ = '2.4.0'
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
__links__ = {
    'discord' : 'https://discord.gg/eRVfbgwNku',
    'releases' : 'https://github.com/wmw-modding/wheres-my-editor/releases/latest',
    'bugs' : 'https://github.com/wmw-modding/wheres-my-editor/issues',
}

__min_wmwpy_version__ = "0.6.0-beta"

import logging
import os
import sys
import platform
from datetime import datetime
import crossplatform
import re

def createLogger(
    type = 'file',
    filename = 'logs/log.log',
    debug = False,
):
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    format = '[%(levelname)s] %(message)s'
    datefmt = '%I:%M:%S %p'
    level = logging.DEBUG if debug else logging.INFO
    # level = logging.CRITICAL

    # filename = 'log.log'
    
    handlers = []

    if type == 'file':
        try:
            os.mkdir('logs')
        except:
            pass
        
        handlers.append(logging.FileHandler(filename))
        format = '[%(asctime)s] [%(levelname)s] %(message)s'

        # logging.basicConfig(filename=filename, filemode='w', format=format, datefmt=datefmt, level=level)
        # logger.info('logging file')
    
    handlers.append(logging.StreamHandler())
    logging.basicConfig(format=format, datefmt=datefmt, level=level, handlers=handlers)
    
    logger = logging.getLogger(__name__)
    logger.info(filename)

def setup_logger(
    name: str,
    dir: str = 'logs',
    extension: str = 'log',
    keep: int = 5,
    debug: bool = False,
):
    log_filename = os.path.join(dir, f'{datetime.now().strftime(name)}.{extension}')
    createLogger('file', filename = log_filename, debug = debug)
    
    if os.path.isdir(dir):
        log_files = os.listdir(dir)
        logs = []
        
        for file in log_files:
            if file == os.path.basename(log_filename):
                continue
            
            try:
                logs.append((datetime.strptime(os.path.splitext(file)[0], name), file))
            except ValueError:
                continue
        
        logs.sort(key = lambda i: i[0])
        
        logs = logs[max(0, keep-1)::]
        
        for log in logs:
            logging.debug(f'deleting log: {log[1]}')
            os.remove(os.path.join(dir, log[1]))
        
    return log_filename
    
_log_filename_format = "%m-%d-%y_%H-%M-%S"

debug = False

if sys.argv[0].endswith('.py'):
    debug = True

args = sys.argv[1::]
if len(args) > 0:
    if args[0] in ['-d', '--debug']:
        debug = True

_log_filename = setup_logger(
    _log_filename_format,
    debug = debug,
)

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkwidgets
from PIL import Image, ImageTk, ImageDraw
from settings import Settings
from lxml import etree
import numpy
import typing
from copy import copy, deepcopy
import pathlib
import webbrowser

import wmwpy
from scrollframe import ScrollFrame
import popups

logging.info(f'wme version: {__version__}')
logging.info(f'wmwpy version: {wmwpy.__version__}')

if wmwpy.__version__ < __min_wmwpy_version__:
    logging.error(f'wmwpy version must be "{__min_wmwpy_version__}" or higher.')
    raise ImportWarning(f'wmwpy version must be "{__min_wmwpy_version__}" or higher.')


# add create_circle and create_circle_arc to canvas
# https://stackoverflow.com/a/17985217/17129659
def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
tk.Canvas.create_circle = _create_circle

def _create_circle_arc(self, x, y, r, **kwargs):
    if "start" in kwargs and "end" in kwargs:
        kwargs["extent"] = kwargs.pop("end") - kwargs["start"]
    return self.create_arc(x-r, y-r, x+r, y+r, **kwargs)
tk.Canvas.create_circle_arc = _create_circle_arc


# WME class
class WME(tk.Tk):
    APP_ICONS = [
            'assets/images/icon_256x256.ico',
        ]
    LOGO = 'assets/images/WME_logo.png'
    ASSETS = {
        'folder_icon': {
            'path': 'assets/images/folder.png',
            'format': 'photo',
            'size': (16,16),
            'cache': None,
        }
    }
    
    def __init__(self, parent):
        tk.Tk.__init__(self,parent)
        self.parent = parent
        
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            self.WME_assets = sys._MEIPASS
        else:
            self.WME_assets = os.path.dirname(__file__)
        
        self.findIcons()
        # if len(self.windowIcons) > 0:
        #     self.iconphoto(True, *self.windowIcons)
        
        try:
            self.iconbitmap(default = list(self.windowIcons.keys())[0])
        except:
            try:
                self.iconphoto(True, *list(self.windowIcons.values()))
            except:
                pass
        
        self.title("Where's my Editor")
        self.geometry('%dx%d' % (760 , 610) )
        self.minsize(500,300)
        
        self.clipboard = None
        
        self.scale = 5
        self.settings = Settings(
            filename = 'settings.json',
            default_settings = {
                'version': 2,
                'game': {
                    'gamepath': '',
                    'assets': '/assets',
                    'game': 'wmw',
                    'default_level': {
                        'xml': '',
                        'image': '',
                    },
                },
                'view': {
                    'radius': True,
                    'PlatinumType': {
                        'platinum': True,
                        'normal': True,
                        'note': True,
                        'none': True,
                    },
                    'path': True,
                }
            }
        )
        self.updateSettings()

        self.selection_rect = None
        
        self.style = ttk.Style()
        
        self.style.layout("Horizontal.TPanedWindow", [('TPanedWindow', {})])

        self.style.layout("Vertical.TPanedWindow", [('TPanedWindow', {})])
        
        # self.style.theme_use('clam')
        
        try:
            self.panedGrip : dict[typing.Literal['image', 'horizontal', 'vertical'], Image.Image | ImageTk.PhotoImage] = {
                'image' : Image.open(self.getAssetPath('assets/images/grip.gif')).convert('RGBA'),
            }

            self.panedGrip['horizontal'] = ImageTk.PhotoImage(self.panedGrip['image'])
            self.panedGrip['vertical'] = ImageTk.PhotoImage(self.panedGrip['image'].rotate(90, expand = True))
        
            self.style.element_create("Sash.Horizontal", "image", self.panedGrip['horizontal'], sticky='we')
            self.style.layout("Horizontal.TPanedWindow", [('Sash.Horizontal', {})])

            self.style.element_create("Sash.Vertical", "image", self.panedGrip['vertical'], sticky='ns')
            self.style.layout("Vertical.TPanedWindow", [('Sash.Vertical', {})])
        
        except:
            logging.exception('Unable to set grip image')
        
        # self.style.layout("Clicked.TPanedWindow", [('Sash.xsash', {})])
        
        self.style.configure('TPanedwindow', opaqueresize=False)
        # self.style.configure('Clicked.TPanedwindow', background='blue')
        self.style.configure('Sash', sashthickness = 5)
        
        # ttk.PanedWindow(orient='horizontal').cget('orient')
        
        # self.bind_class('TPanedwindow', '<Button-1>', lambda e : print(e.widget.configure(style = 'Clicked.TPanedwindow')))
        # self.bind_class('TPanedwindow', '<B1-Motion>', lambda e : e.widget.tk.call(e.widget, "sash", 0, (e.x if str(e.widget["orient"]) == "horizontal" else e.y)))
        # self.bind_class('TPanedwindow', '<ButtonRelease-1>', lambda e : e.widget.configure(style = 'TPanedwindow'))
        # self.bind_class('Sash.TPanedWindow', '<Leave>', lambda e : e.widget.configure(style = 'TPanedwindow'))
        # self.bind_class('Sash.TPanedWindow', '<Enter>', lambda e : e.widget.configure(style = 'Clicked.TPanedwindow'))

        self.active = True

        self.selectedObject: wmwpy.classes.Object | None = None
        self.selectedPart: dict[
            typing.Literal[
                'type',
                'id',
                'property'
            ], str | None,
        ] = {
            'type': None,
            'id': None,
            'property': None,
        }
        self.dragInfo: dict[typing.Literal['offset'], tuple[float, float]] = {
            'offset': (0, 0),
        }
        self.level : wmwpy.classes.Level = None
        self.game : wmwpy.Game = None
        
        self.createMenubar()
        self.createWindow()
        self.objectContextMenu = tk.Menu(self.level_canvas, tearoff = 0)
        
        self.loadGame()
        
        if self.game != None:
            self.loadLevel(
                self.settings.get('game.default_level.xml'),
                self.settings.get('game.default_level.image')
            )
        
        self.protocol("WM_DELETE_WINDOW", self.close)
    
    def getAssetPath(self, path : str):
        return os.path.join(self.WME_assets, path)
    
    def getAsset(self, name: str) -> typing.Any:
        info = self.ASSETS[name]
        if info.get('cache'):
            return info.get('cache')
        else:
            path = self.getAssetPath(info['path'])
            logging.debug(f'asset format: {info["format"]}')
            size = info.get('size')
            if info['format'] == 'image':
                info['cache'] = Image.open(path)
                if size:
                    info['cache'] = info['cache'].resize(size)
            elif info['format'] == 'photo':
                image = Image.open(path)
                if size:
                    image = image.resize(size)
                info['cache'] = ImageTk.PhotoImage(image)
            elif info['format'] == 'bitmap':
                image = Image.open(path)
                if size:
                    image = image.resize(size)
                info['cache'] = ImageTk.BitmapImage(image.convert('1'), foreground = 'black')
            elif info['format'] == 'bytes':
                info['cache'] = None
                with open(path, 'rb') as file:
                    info['cache'] = file.read()
            else:
                info['cache'] = None
                with open(path, 'r') as file:
                    info['cache'] = file.read()
            
            return info['cache']
    
    def findIcons(self):
        self.windowIcons : dict[str, ImageTk.PhotoImage] = {}
        
        for icon in self.APP_ICONS:
            try:
                self.windowIcons[self.getAssetPath(icon)] = ImageTk.PhotoImage(
                        Image.open(self.getAssetPath(icon))
                    )
                
            except:
                logging.exception('cannot load icon')
        
        return self.windowIcons

    def createWindow(self):
        self.separator = ttk.PanedWindow(orient='horizontal', style = 'Horizontal.TPanedWindow')
        self.separator.pack(fill=tk.BOTH, expand=1)

        self.side_pane = ttk.PanedWindow(self.separator, orient='vertical', style = "Vertical.TPanedWindow")
        self.separator.add(self.side_pane)
        
        side_pane_width = 250
        side_pane_height = 300
        
        
        # create object selector
        
        self.object_selector : dict[typing.Literal[
            'labelFrame',
            'treeview',
            'y_scroll',
            'x_scroll',
            'menu',
        ], tk.Widget | ttk.Treeview | tk.Menu] = {
            'labelFrame' : ttk.LabelFrame(self.side_pane, width=side_pane_width, height=side_pane_height, text='Objects'),
            'treeview' : None,
            'y_scroll' : None,
            'x_scroll' : None,
            'menu': None,
        }
        self.side_pane.add(self.object_selector['labelFrame'])
        
        self.object_selector['treeview'] = ttk.Treeview(
            self.object_selector['labelFrame'],
            show = 'headings',
            name = 'objects',
            columns = ['name', 'type'],
        )
        self.object_selector['treeview'].heading('type', text='Type', anchor='w')
        self.object_selector['treeview'].heading('name', text='Name', anchor='w')
        self.object_selector['treeview'].column('type', width=1)
        self.object_selector['treeview'].column('name', width=1)
        
        self.object_selector['treeview'].pack(side='left', fill='both', expand = True)

        self.object_selector['menu'] = tk.Menu(self.object_selector['treeview'], tearoff = 0)
        
        self.object_selector['y_scroll'] = ttk.Scrollbar(
            self.object_selector['labelFrame'],
            orient='vertical',
            command = self.object_selector['treeview'].yview
        )
        
        self.object_selector['treeview'].configure(yscrollcommand = self.object_selector['y_scroll'].set)
        
        self.object_selector['y_scroll'].pack(side='right', fill='y')
        
        self.properties : dict[typing.Literal[
            'labelFrame',
            'notebook',
            'scrollFrame',
            'frame',
            'panned',
            'left',
            'right',
            'title',
        ], tk.Widget, tk.StringVar] = {
            'title': tk.StringVar(value = 'Properties'),
            'labelFrame' : ttk.LabelFrame(
                self.side_pane,
                width = side_pane_width,
                height = side_pane_height,
                text = 'Properties',
            )
        }
        self.properties['title'].trace_add(
            'write',
            lambda *args: self.properties['labelFrame'].configure(text = self.properties['title'].get()),
        )
        
        self.properties['labelFrame'].configure
        self.side_pane.add(self.properties['labelFrame'])
        
        # self.properties['notebook'] = ttk.Notebook(self.properties['labelFrame'])
        
        self.properties['scrollFrame'] = ScrollFrame(self.properties['labelFrame'], usettk=True, width=side_pane_width,)
        # self.properties['notebook'].pack(fill='both', expand=True)
        # self.properties['notebook'].add(self.properties['scrollFrame'], text='Object Properties')
        # self.properties['notebook'].add(ttk.Frame(self.properties['notebook']), text='Level Properties')
        self.properties['scrollFrame'].pack(fill='both', expand=True)
        self.properties['frame'] = self.properties['scrollFrame'].viewPort

        self.level_canvas = tk.Canvas(self.separator, width=90*self.scale, height=120*self.scale)
        self.separator.add(self.level_canvas, weight=1)
        
        self.level_images = {
            'background': self.level_canvas.create_image(
                0,0,
                anchor = 'c',
                image = None,
                tag = 'level',
            ),
            'objects': {}
        }
        
        self.level_scrollbars = {
            'horizontal' : ttk.Scrollbar(
                self.level_canvas,
                orient='horizontal',
                command = self.level_canvas.xview
            ),
            'vertical' : ttk.Scrollbar(
                self.level_canvas,
                orient='vertical',
                command = self.level_canvas.yview
            ),
        }
        
        self.level_scrollbars['horizontal'].pack(side='bottom', fill='x')
        self.level_scrollbars['vertical'].pack(side='right', fill='y')
        
        self.level_canvas.configure(xscrollcommand=self.level_scrollbars['horizontal'].set)
        self.level_canvas.configure(yscrollcommand=self.level_scrollbars['vertical'].set)
        
        
        self.createLevelContextMenu()
        
        self.resetProperties()
        self.createProgressBar()
    
    def enableWindow(self):
        self.bind(f'<{crossplatform.modifier()}-s>', self.saveLevel)
        self.bind(f'<{crossplatform.modifier()}-S>', self.saveLevelAs)
        self.bind(f'<{crossplatform.modifier()}-o>', self.openLevel)
        
        if platform.system() == 'Linux':
            self.level_canvas.bind("<Button-4>", self.onLevelMouseWheel)
            self.level_canvas.bind("<Button-5>", self.onLevelMouseWheel)
            
            self.level_canvas.bind("<Shift-Button-4>", lambda *args: self.onLevelMouseWheel(*args, type = 1))
            self.level_canvas.bind("<Shift-Button-5>", lambda *args: self.onLevelMouseWheel(*args, type = 1))
        else:
            self.level_canvas.bind("<MouseWheel>", self.onLevelMouseWheel)
            self.level_canvas.bind("<Shift-MouseWheel>", lambda *args: self.onLevelMouseWheel(*args, type = 1))
        
        self.level_canvas.bind('<Button-1>', self.onLevelClick)
        self.level_canvas.bind('<Button1-Motion>', self.onLevelMove)
        
        self.level_canvas.bind('<Enter>', self.bindKeyboardShortcuts)
        self.level_canvas.bind('<Leave>', self.unbindKeyboardShortcuts)
        
        if platform.system() == 'Darwin':
            self.level_canvas.bind('<Button-2>', self.onLevelRightClick)
        else:
            self.level_canvas.bind('<Button-3>', self.onLevelRightClick)
        
        self.object_selector['treeview'].configure(selectmode = 'browse')
        self.object_selector['treeview'].state(("!disabled",))
        # re-enable item opening on click
        self.object_selector['treeview'].unbind('<Button-1>')
        
        items = self.menubar.index('end')
        
        for item in range(items):
            self.menubar.entryconfig(item + 1, state = 'normal')
        
        self.updateLevel()
        
        self.bindKeyboardShortcuts()
    
    def disableWindow(self):
        self.unbind(f'<{crossplatform.modifier()}-s>')
        self.unbind(f'<{crossplatform.modifier()}-S>')
        self.unbind(f'<{crossplatform.modifier()}-o>')
        
        if platform.system() == 'Linux':
            self.level_canvas.unbind("<Button-4>")
            self.level_canvas.unbind("<Button-5>")
            
            self.level_canvas.unbind("<Shift-Button-4>")
            self.level_canvas.unbind("<Shift-Button-5>")
        else:
            self.level_canvas.unbind("<MouseWheel>")
            self.level_canvas.unbind("<Shift-MouseWheel>")
            
        self.level_canvas.unbind('<Button-1>')
        self.level_canvas.unbind('<Button1-Motion>')
        
        if platform.system() == 'Darwin':
            self.level_canvas.unbind('<Button-2>')
        else:
            self.level_canvas.unbind('<Button-3>')
        
        self.level_canvas.unbind('<Enter>')
        self.level_canvas.unbind('<Leave>')
        self.unbindKeyboardShortcuts()
        
        objects = self.level_canvas.find_withtag('object')
        objects = list(objects) + list(self.level_canvas.find_withtag('selection'))
        
        for id in objects:
            self.unbindObject(id)
        
        self.object_selector['treeview'].configure(selectmode = 'none')
        
        self.object_selector['treeview'].state(("disabled",))
        # disable item opening on click
        self.object_selector['treeview'].bind('<Button-1>', lambda e: 'break')
        
        items = self.menubar.index('end')
        
        for item in range(items):
            self.menubar.entryconfig(item + 1, state = 'disabled')
    
    def bindKeyboardShortcuts(self, *args):
        logging.debug('Binding keyboard shortcuts')
        
        self.bind(f'<{crossplatform.modifier()}-v>', self.pasteObject)
        self.bind(f'<{crossplatform.modifier()}-c>', self.copyObject)
        self.bind(f'<{crossplatform.modifier()}-x>', self.cutObject)
        self.bind('<KeyPress-Delete>', self.deleteObject)
        
        self.bind('<Up>', lambda *args : self.moveObject(amount = (0,1)))
        self.bind('<Down>', lambda *args : self.moveObject(amount = (0,-1)))
        self.bind('<Left>', lambda *args : self.moveObject(amount = (-1,0)))
        self.bind('<Right>', lambda *args : self.moveObject(amount = (1,0)))
        
        self.bind(f'<{crossplatform.modifier()}-Up>', lambda *args : self.moveObject(amount = (0,0.5)))
        self.bind(f'<{crossplatform.modifier()}-Down>', lambda *args : self.moveObject(amount = (0,-0.5)))
        self.bind(f'<{crossplatform.modifier()}-Left>', lambda *args : self.moveObject(amount = (-0.5,0)))
        self.bind(f'<{crossplatform.modifier()}-Right>', lambda *args : self.moveObject(amount = (0.5,0)))
        
        self.bind(f'<Alt-Up>', lambda *args : self.moveObject(amount = (0,0.1)))
        self.bind(f'<Alt-Down>', lambda *args : self.moveObject(amount = (0,-0.1)))
        self.bind(f'<Alt-Left>', lambda *args : self.moveObject(amount = (-0.1,0)))
        self.bind(f'<Alt-Right>', lambda *args : self.moveObject(amount = (0.1,0)))
        
        self.bind(f'<Shift-Up>', lambda *args : self.moveObject(amount = (0,4)))
        self.bind(f'<Shift-Down>', lambda *args : self.moveObject(amount = (0,-4)))
        self.bind(f'<Shift-Left>', lambda *args : self.moveObject(amount = (-4,0)))
        self.bind(f'<Shift-Right>', lambda *args : self.moveObject(amount = (4,0)))
    
    def unbindKeyboardShortcuts(self, *args):
        logging.debug('unbinding keyboard shortcuts')
        
        self.unbind(f'<{crossplatform.modifier()}-v>')
        self.unbind(f'<{crossplatform.modifier()}-c>')
        self.unbind(f'<{crossplatform.modifier()}-x>')
        self.unbind('<KeyPress-Delete>')
        
        self.unbind('<Up>')
        self.unbind('<Down>')
        self.unbind('<Left>')
        self.unbind('<Right>')
        
        self.unbind(f'<{crossplatform.modifier()}-Up>')
        self.unbind(f'<{crossplatform.modifier()}-Down>')
        self.unbind(f'<{crossplatform.modifier()}-Left>')
        self.unbind(f'<{crossplatform.modifier()}-Right>')
        
        self.unbind(f'<Alt-Up>')
        self.unbind(f'<Alt-Down>')
        self.unbind(f'<Alt-Left>')
        self.unbind(f'<Alt-Right>')
        
        self.unbind(f'<Shift-Up>')
        self.unbind(f'<Shift-Down>')
        self.unbind(f'<Shift-Left>')
        self.unbind(f'<Shift-Right>')
    
    def createProgressBar(self):
        self.progress_bar : dict[typing.Literal[
            'frame',
            'progress_bar',
            'label',
            'var',
        ],
           ttk.Frame |
           ttk.Progressbar |
           ttk.Label |
           tk.StringVar
        ] = {}
        
        self.progress_bar['frame'] = ttk.Frame()
        self.progress_bar['frame'].pack(side = 'bottom', fill = 'x')
        
        self.progress_bar['var'] = tk.StringVar()
        
        self.progress_bar['progress_bar'] = ttk.Progressbar(
            self.progress_bar['frame'],
        )
        self.progress_bar['label'] = ttk.Label(
            self.progress_bar['frame'],
            textvariable = self.progress_bar['var'],
        )
        
        self.progress_bar['progress_bar'].grid(column = 0, row = 0, sticky = 'we')
        self.progress_bar['label'].grid(column = 1, row = 0, sticky = 'we')
        
        self.progress_bar['frame'].columnconfigure(0, weight = 1, uniform = 'progress_bar')
        self.progress_bar['frame'].columnconfigure(1, weight = 2, uniform = 'progress_bar')
    
    def updateProgressBar(
        self,
        progress : int = 0,
        text : str = '',
        max : int = None,
    ):
        self.progress_bar['var'].set(text)
        if max != None:
            self.progress_bar['progress_bar']['max'] = max
        self.progress_bar['progress_bar']['value'] = progress

        self.update()

    @property
    def state(self) -> typing.Literal['enabled', 'normal', 'disabled']:
        try:
            return self._state
        except:
            return 'enabled'
    @state.setter
    def state(self, state : typing.Literal['enabled', 'normal', 'disabled']):
        if state == 'enabled':
            state = 'normal'
        elif state not in ['enabled', 'normal', 'disabled']:
            raise ValueError(f'unknown state {state}')
        
        self._state = state

        if self._state == 'normal':
            self.enableWindow()
        elif self._state == 'disabled':
            self.disableWindow()
    
    def setState(self, state : typing.Literal['normal', 'disabled']):
        self.level_canvas.configure(state = state)
    
    def onLevelMouseWheel(self, event : tk.Event, type = 0):
        if type:
            scroll = self.level_canvas.xview_scroll
        else:
            scroll = self.level_canvas.yview_scroll
        
        if platform.system() == 'Windows':
            scroll(int(-1* (event.delta/120)), "units")
        elif platform.system() == 'Darwin':
            scroll(int(-1 * event.delta), "units")
        else:
            if event.num == 4:
                scroll( -1, "units" )
            elif event.num == 5:
                scroll( 1, "units" )
    
    OBJECT_MULTIPLIER = 1.25
    
    def updateLayers(self):
        objects = self.level_canvas.find_withtag('object')
        if len(objects) < 0:
            return
        
        def raise_tag(bottom, top):
            objects = self.level_canvas.find_withtag(top)
            if len(objects):
                self.level_canvas.tag_raise(top, bottom)
                return top
            return bottom
        
        order = [
            'level',
            *[f'object&&object-{obj.id}' for obj in self.level.objects],
            'background',
            'foreground',
            'selection',
            'radius',
            'pathLine',
            'pathPoint',
        ]
        
        last_tag = order[0]
        
        for tag in order[1::]:
            last_tag = raise_tag(last_tag, tag)
        
        # for obj in self.level.objects:
        #     obj_id = f'object-{obj.id}'
        #     last_tag = raise_tag(last_tag, f'object&&{obj_id}')
        # 
        # last_tag = raise_tag(last_tag, 'background')
        # last_tag = raise_tag(last_tag, 'foreground')
        # 
        # for visualization_tag in self.settings.get('view', {}):
        #     logging.debug(f'visualization tag: {visualization_tag}')
        #     last_tag = raise_tag(last_tag, visualization_tag)
        # 
        # raise_tag('pathLine', 'pathPoint')
        # 
        # if len(self.level_canvas.find_withtag('selection')) > 0:
        #     last_tag = raise_tag('object', 'selection')
    
    SELECTION_BORDER_WIDTH = 2
    
    def updateSelectionRectangle(self, obj : wmwpy.classes.Object | None = None):
        if obj == None:
            obj = self.selectedObject
        if obj == None:
            self.level_canvas.delete('selection')
            # logging.info('deleted selection')
            return
        
        obj_id = f'object-{str(obj.id)}'
        
        platinum_type = obj.properties.get('PlatinumType', obj.defaultProperties.get('PlatinumType', 'none'))

        if not self.settings.get(['view.PlatinumType', platinum_type], True):
            self.level_canvas.delete('selection')
            return
        
        pos = numpy.array(obj.pos)
        size = numpy.maximum(numpy.array(obj.size), [1,1])
        logging.debug(f'object size: {size}')
        
        selectionImage = Image.new('RGBA', tuple(size * obj.scale), 'black')
        selectionImageDraw = ImageDraw.Draw(selectionImage)
        logging.debug(f'image size: {selectionImage.size}')
        logging.debug(f'rectangle size: {(0,0) + tuple(numpy.array(selectionImage.size) - (self.SELECTION_BORDER_WIDTH - 1))}')
        selectionImageDraw.rectangle(
            (0,0) + tuple(numpy.array(selectionImage.size) - (self.SELECTION_BORDER_WIDTH - 1)),
            fill = '#0000',
            outline = 'black',
            width = self.SELECTION_BORDER_WIDTH,
        )
        selectionImage = obj.rotateImage(selectionImage)
        self.selectionPhotoImage = ImageTk.PhotoImage(selectionImage)
        
        pos = self.getObjectPosition(pos, obj.offset)
        
        id = self.level_canvas.find_withtag('selection')
        if len(id) <= 0:
            self.level_canvas.create_image(
                *pos,
                image = self.selectionPhotoImage,
                tags = 'selection'
            )
        else:
            self.level_canvas.itemconfig(
                id,
                image = self.selectionPhotoImage
            )
            self.level_canvas.coords(
                id,
                *pos
            )
        
    
        self.bindObject(id, obj)
        
    def getObjectPosition(self, pos = (0,0), offset  = (0,0)):
        pos = numpy.array(pos)
        offset = numpy.array(offset)
        
        pos = pos - offset
        pos = self.toLevelCanvasCoord(pos)
        
        return pos
    
    def toLevelCanvasCoord(self, pos: int | float | numpy.ndarray, multiplier: float | int = OBJECT_MULTIPLIER) -> float | numpy.ndarray:
        if isinstance(pos, (int,float)):
            return (pos * multiplier) * self.level.scale
        else:
            return (pos * numpy.array([multiplier, -multiplier])) * self.level.scale
    
    def updateObject(self, obj : wmwpy.classes.Object | None):
        if obj == None:
            self.updateSelectionRectangle()
            self.updateLevelScroll()
            return
        
        offset = numpy.array(obj.offset)
        canvas_pos = numpy.array(obj.pos)
        canvas_pos = self.getObjectPosition(canvas_pos, offset)
        true_pos = self.getObjectPosition(obj.pos)
        
        id = f'object-{str(obj.id)}'
        
        platinum_type = obj.properties.get('PlatinumType', obj.defaultProperties.get('PlatinumType', 'none'))

        if not self.settings.get(['view.PlatinumType', platinum_type], True):
            self.level_canvas.delete(id)
            return
        
        items = self.level_canvas.find_withtag(id)
        
        logging.debug(f'items: {items}')
        
        background = None
        foreground = None
        
        for item in items:
            tags = self.level_canvas.gettags(item)
            logging.debug(f'tags: {tags}')
            if 'background' in tags:
                background = item
            elif 'foreground' in tags:
                foreground = item
        
        self.level_canvas.delete(f'radius&&{id}')
        self.level_canvas.delete(f'path&&{id}')
        
        if len(items) > 0:
            if background:
                self.level_canvas.coords(
                    background,
                    canvas_pos[0],
                    canvas_pos[1],
                )
                self.level_canvas.itemconfig(
                    background,
                    image = obj.background_PhotoImage,
                )
            
            if foreground:
                self.level_canvas.coords(
                    foreground,
                    canvas_pos[0],
                    canvas_pos[1],
                )
                self.level_canvas.itemconfig(
                    foreground,
                    image = obj.foreground_PhotoImage,
                )
        else:
            if len(obj._background) > 0:
                self.level_canvas.create_image(
                    canvas_pos[0],
                    canvas_pos[1],
                    anchor = 'c',
                    image = obj.background_PhotoImage,
                    tags = ('object', 'background', id),
                )
                
            if len(obj._foreground) > 0:
                self.level_canvas.create_image(
                    canvas_pos[0],
                    canvas_pos[1],
                    anchor = 'c',
                    image = obj.foreground_PhotoImage,
                    tags = ('object', 'foreground', id)
                )
            
            if len(obj._foreground) == 0 and len(obj._background) == 0:
                self.level_canvas.create_image(
                    canvas_pos[0],
                    canvas_pos[1],
                    anchor = 'c',
                    image = ImageTk.PhotoImage(Image.new('RGBA', (1, 1), 'black')),
                    tags = ('object', 'foreground', id),
                )
        
        if (obj == self.selectedObject or self.settings.get('view.radius', True)) and obj.Type is not None:
            properties = filter(lambda name : obj.Type.PROPERTIES[name].get('type', 'string') == 'radius', obj.Type.PROPERTIES)
            
            for property in properties:
                props = obj.Type.get_properties(property)
                for name, radius in props.items():
                    logging.debug(f'radius: {radius}')
                    radius_canvas_size = self.toLevelCanvasCoord(radius)
                    if radius_canvas_size > 0:
                        r_id = self.level_canvas.create_circle(
                            true_pos[0],
                            true_pos[1],
                            radius_canvas_size,
                            fill = '',
                            outline = 'red',
                            width = self.OBJECT_MULTIPLIER,
                            tags = ('passthrough', 'part', 'radius', property, id),
                        )
                        
                        logging.debug(f'radius tags: {self.level_canvas.gettags(r_id)}')
        
        if (obj == self.selectedObject or self.settings.get('view.path', True)) and obj.Type is not None:
            path_points = obj.Type.get_properties('PathPos#')
            logging.debug(f'path_points: {path_points}')
            if isinstance(path_points, dict) and len(path_points) > 0:
                is_global = obj.Type.get_property('PathIsGlobal')
                is_closed = obj.Type.get_property('PathIsClosed')

                if is_global:
                    path_start = obj.pos
                else:
                    path_start = (0, 0)
                
                path_canvas_points = []

                for property, path_point in path_points.items():
                    logging.debug(f'property: {property}')
                    logging.debug(f'value: {path_point}')
                    path_pos = copy(path_start)
                        
                    if isinstance(path_point, list):
                        if len(path_point) == 1:
                            path_point += [path_start[1]]
                            path_pos = tuple(path_point)
                        elif len(path_point) >= 2:
                            path_pos = (path_point[0], path_point[1])
                    
                    path_pos = numpy.array(path_pos)
                    
                    global_pos = copy(canvas_pos)
                    if is_global:
                        global_pos = self.toLevelCanvasCoord(path_pos)
                    else:
                        # global_pos = self.getObjectPosition(obj.pos) + path_pos
                        global_pos = self.toLevelCanvasCoord(obj.pos) + self.toLevelCanvasCoord(path_pos, 1)
                    
                    path_canvas_points.append(tuple(global_pos))
                    
                    color = 'black'
                    if obj == self.selectedObject and self.selectedPart['property'] == property:
                        color = 'yellow'
                    
                    point_id = self.level_canvas.create_circle(
                        global_pos[0],
                        global_pos[1],
                        3,
                        fill = color,
                        outline = '',
                        tags = ('part', 'path', property, 'pathPoint', id),
                    )

                if len(path_canvas_points) > 1:
                    if is_closed:
                        line = self.level_canvas.create_polygon(
                            path_canvas_points,
                            fill = '',
                            outline = 'black',
                            width = 2,
                            tags = ('passthrough', 'part', 'path', property, 'pathLine', id),
                        )
                    else:
                        line = self.level_canvas.create_line(
                            path_canvas_points,
                            fill = 'black',
                            width = 2,
                            tags = ('passthrough', 'part', 'path', property, 'pathLine', id),
                        )
                
                # self.level_canvas.tag_bind(line, '<Button-1>', self.onLevelClick)
        
        # logging.info(f"id: {id}")
        # logging.info(f"pos: {pos}\n")
        
        self.updateLayers()
        
        self.bindObject(f'object&&{id}', obj)
        
        
        self.updateSelectionRectangle()
        self.updateLevelScroll()
    
    
    def selectObjectAt(
        self,
        pos: tuple[float, float] | list[float] | tk.Event,
        halo: int | float = 5,
    ):
        event = None
        if isinstance(pos, tk.Event):
            event = pos
            logging.debug(f'select obj event: {event.__dict__}')
            pos = (pos.x, pos.y)

            pos = (
                self.level_canvas.canvasx(pos[0]),
                self.level_canvas.canvasy(pos[1])
            )
        
        # objects = self.level_canvas.find_overlapping(*mouse, *mouse)
        objects = self.level_canvas.find_overlapping(
            pos[0] - halo, pos[1] - halo,
            pos[0] + halo, pos[1] + halo,
        )
        logging.debug(f'under mouse: {objects}')
        
        for id in reversed(objects):
            tags = self.level_canvas.gettags(id)
            logging.debug(f'tags: {tags}')
            if tags[0] in ['selection', 'level']:
                continue
            
            obj_tag = -1
            if not tags[obj_tag].startswith('object-'):
                logging.debug(f'tag not obj: {tags}')
                obj_tag = -2
            
            if tags[obj_tag].startswith('object-'):
                obj = self.level.getObjectById(tags[obj_tag][7::])
                logging.debug(f'obj: {obj}')
                if obj == None:
                    continue
                else:
                    logging.debug(f'obj name: {obj.name}')
            else:
                continue
            
            if tags[0] == 'passthrough':
                continue
            elif tags[0] == 'object':
                logging.debug(f'selecting obj: {obj.name}')
                self.selectObject(obj, event)
                return 'object', obj
            elif tags[0] == 'part':
                self.selectPart(
                    obj,
                    tags[1],
                    id,
                    tags[2],
                )
                return 'part', obj, self.selectedPart
        
        self.selectObject(None)
        
        return None, None
    
    def onLevelClick(self, event : tk.Event):
        logging.debug('level')
        
        if self.level == None:
            return
        
        self.selectObjectAt(event)
            
            
    
    def onLevelMove(self, event: tk.Event):
        if self.selectedPart['type'] != None:
            self.dragPart(event)
        elif self.selectedObject:
            self.dragObject(self.selectedObject, event)
        
    
    def createLevelContextMenu(self):
        self.levelContextMenu = tk.Menu(self.level_canvas, tearoff = 0)
        self.levelContextMenu.add_command(label = 'add object', command = lambda *args: self.addObjectSelector(self.getRelativeMousePos(self.level_canvas.winfo_pointerxy(), self.level_canvas)))
        self.levelContextMenu.add_command(label = 'paste', command = self.pasteObject, accelerator = f'{crossplatform.shortModifier()}+V')
    
    def onLevelRightClick(self, event):
        logging.debug('level context menu')
        
        selected_type, selected_obj, *extra = self.selectObjectAt(event)
        
        if selected_type == None:
            self.showPopup(self.levelContextMenu, event)
        elif selected_type == 'object':
            self.showPopup(self.createObjectContextMenu(selected_obj), event)
        elif selected_type == 'part':
            self.showPopup(self.createPartContextMenu(selected_obj, extra[0]), event)
            
    
    def bindObject(self, id, obj : wmwpy.classes.Object | None = None):
        if obj == None:
            if self.selectedObject != None:
                obj = self.selectedObject
            else:
                return
        
        # self.level_canvas.tag_bind(
        #     id,
        #     '<Button1-Motion>',
        #     lambda e, object = obj: self.dragObject(object, e)
        # )
        
        context_menu = self.createObjectContextMenu(obj)
        
        # if platform.system() == 'Darwin':
        #     self.level_canvas.tag_bind(
        #         id,
        #         '<Button-2>',
        #         lambda e, object = obj, menu = context_menu: self.showPopup(menu, e, callback = lambda : self.selectObject(object))
        #     )
        # else:
        #     self.level_canvas.tag_bind(
        #         id,
        #         '<Button-3>',
        #         lambda e, object = obj, menu = context_menu: self.showPopup(menu, e, callback = lambda : self.selectObject(object))
        #     )
    
    def unbindObject(self, id):
        self.level_canvas.tag_unbind(
            id,
            '<Button1-Motion>',
        )
        self.level_canvas.tag_unbind(
            id,
            '<Button-1>',
        )
        
        if platform.system() == 'Darwin':
            self.level_canvas.tag_unbind(
                id,
                '<Button-2>',
            )
        else:
            self.level_canvas.tag_unbind(
                id,
                '<Button-3>',
            )
        
    def createObjectContextMenu(self, obj : wmwpy.classes.Object):
        self.objectContextMenu.delete(0, 3)
        self.objectContextMenu.add_command(label = 'copy', command = lambda *args : self.copyObject(obj), accelerator = f'{crossplatform.shortModifier()}+C')
        self.objectContextMenu.add_command(label = 'cut', command = lambda *args : self.cutObject(obj), accelerator = f'{crossplatform.shortModifier()}+X')
        self.objectContextMenu.add_command(label = 'delete', command = lambda *args : self.deleteObject(obj), accelerator = 'Del')
        
        return self.objectContextMenu

    def createPartContextMenu(
        self,
        obj: wmwpy.classes.Object,
        part: dict[
            typing.Literal[
                'type',
                'id',
                'property'
            ], str | None,
        ],
        ):
        
        self.objectContextMenu.delete(0, 3)
        self.objectContextMenu.add_command(label = 'delete', command = lambda *args : self.deleteProperty(obj, part['property']), accelerator = 'Del')
        
        return self.objectContextMenu
    
    def showPopup(self, menu : tk.Menu, event : tk.Event = None, callback : typing.Callable = None):
        try:
            if callback != None:
                callback()
            menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            menu.grab_release()
    
    def moveObject(self, obj : wmwpy.classes.Object | None = None, amount : tuple[float,float] = (0,0)) -> tuple[float,float]:
        if not self.checkLevelFocus():
            return
        
        if (obj == None) or isinstance(obj, tk.Event):
            obj = self.selectedObject
        
        if self.selectedPart['type']:
            self.dragPart(
                obj = obj,
                amount = amount,
            )
        else:
            if obj == None:
                return
            
            amount = numpy.array(amount)
            pos = tuple(obj.pos + amount)
            obj.pos = pos
            self.updateObject(obj)
            
            if self.selectedObject == obj:
                if 'pos' in self.objectProperties:
                    self.objectProperties['pos']['var'][0].set(pos[0])
                    self.objectProperties['pos']['var'][1].set(pos[1])
        
            return pos
    
    def deleteObject(self, obj : wmwpy.classes.Object = None):
        if (obj == None) or isinstance(obj, tk.Event):
            if isinstance(obj, tk.Event):
                if not self.checkLevelFocus():
                    return

            obj = self.selectedObject
        
        if obj == None:
            return
        
        if self.selectedPart['type']:
            self.deleteProperty(obj, self.selectedPart['property'])
        else:
            self.level_canvas.delete(f'object-{str(obj.id)}')
            
            if obj in self.level.objects:
                index = self.level.objects.index(obj)
                del self.level.objects[index]
            
            if obj == self.selectedObject:
                self.selectObject(None)
            
            self.updateObjectSelector()
    
    def deleteProperty(self, obj: wmwpy.classes.Object, property: str):
        if property in obj.properties:
            del obj.properties[property]

            self.updateObject(obj)
            if self.selectedObject == obj:
                self.updateProperties()
    
    def checkLevelFocus(
        self,
    ):
        focus = self.focus_get()
        return not isinstance(focus, tk.Entry)
        
    
    def copyObject(
        self,
        obj : wmwpy.classes.Object | None = None,
    ):
        if not self.checkLevelFocus():
            return
        
        if (obj == None) or isinstance(obj, tk.Event):
            obj = self.selectedObject
        
        if obj == None:
            return

        self.clipboard : wmwpy.classes.Object = obj.copy()
    
    def cutObject(
        self,
        obj : wmwpy.classes.Object = None,
    ):
        if not self.checkLevelFocus():
            return
        
        if (obj == None) or isinstance(obj, tk.Event):
            obj = self.selectedObject
        
        if obj == None:
            return
        
        self.copyObject(obj)
        self.deleteObject(obj)
    
    def pasteObject(
        self,
        pos : tuple[int,int] = None,
    ):
        if not self.checkLevelFocus():
            return
        
        if pos == None or isinstance(pos, tk.Event):
            pos = self.getRelativeMousePos(self.level_canvas.winfo_pointerxy(), self.level_canvas)
        
        if isinstance(self.clipboard, wmwpy.classes.Object):
            self.selectObject(
                self.addObject(
                    self.clipboard.copy(),
                    pos = self.windowPosToWMWPos(pos),
                    name = self.clipboard.name,
                )
            )
    
    def addObject(
        self,
        obj : wmwpy.classes.Object | str,
        properties: dict = {},
        pos: tuple[float, float] = (0, 0),
        name: str = 'Obj',
    ):
        if not isinstance(obj, (wmwpy.classes.Object, wmwpy.filesystem.File)):
            obj = self.getFile(obj)
        
        obj = self.level.addObject(
            filename = obj,
            properties = properties,
            pos = pos,
            name = name,
        )
        
        self.updateObject(obj)
        self.updateObjectSelector()
        
        return obj

    def changeObjectFilename(
        self,
        obj: wmwpy.classes.Object,
        new_path: str | None,
    ):
        if obj not in self.level.objects:
            return
        
        level_index = self.level.objects.index(obj)
        
        if new_path == None:
            new_path = filedialog.askopenfilename(
                defaultextension = '.hs',
                filetypes = (
                    ('WMW Object', '*.hs'),
                    ('Any', '*.*'),
                ),
                initialdir = wmwpy.utils.path.joinPath(
                    self.game.gamepath,
                    self.game.assets,
                    self.game.baseassets,
                    'Objects'
                ),
            )
        
        if new_path == None:
            return
        
        if not isinstance(new_path, (wmwpy.filesystem.File)):
            new_path = self.getFile(new_path)
        
        if new_path == None:
            return
        
        self.level.objects.remove(obj)
        
        new_obj = self.level.addObject(
            new_path,
            properties = deepcopy(obj.properties),
            pos = copy(obj.pos),
            name = obj.name,
        )
        
        self.level.objects.insert(level_index, self.level.objects.pop(self.level.objects.index(new_obj)))

        
        self.updateObject(new_obj)
        self.updateObjectSelector()
        if self.selectedObject == obj:
            self.selectObject(new_obj)
        
        return new_obj
    
    def addObjectSelector(self, pos : tuple = (0,0)):
        filename = filedialog.askopenfilename(
            defaultextension = '.hs',
            filetypes = (
                ('WMW Object', '*.hs'),
                ('Any', '*.*'),
            ),
            initialdir = wmwpy.utils.path.joinPath(
                self.game.gamepath,
                self.game.assets,
                self.game.baseassets,
                'Objects'
            ),
        )
        
        self.addObject(
            filename,
            pos = self.windowPosToWMWPos(pos)
        )
    
    def updateProperties(self, obj : wmwpy.classes.Object | None = None):
        if obj == None:
            obj = self.selectedObject
        
        self.resetProperties()

        isLevel = False
        
        if obj == None:
            # no object
            logging.debug('level properties')
            isLevel = True
            obj = self.level
            
            if obj == None:
                self.properties['panned'].configure(height = 1)
                self.properties['scrollFrame'].resetCanvasScroll()
                return
            
        if isLevel:
            self.properties['title'].set('Level Properties')
        else:
            self.properties['title'].set('Properties')
        
        def addProperty(
            property: str,
            value: str,
            type: typing.Literal['number', 'text'] = 'text',
            show_button = True,
            row = 0,
            label_prefix: str = '',
            label_editable: bool = True,
            update_on_entry_edit: bool = True,
            entry_callback: typing.Callable[[str], typing.Any] = None,
            label_callback: typing.Callable[[str], bool] = None,
            button_callback: typing.Callable[[list[tk.StringVar]], str | list[str] | None] = None,
            button_text: str = '-',
            options: list[str] = None,
            label_color: str | tuple = None,
            button_image: tk.PhotoImage = None,
            button_bitmap: tk.BitmapImage = None,
            **kwargs,
        ) -> dict[typing.Literal[
            'label',
            'inputs',
            'button',
            'size',
            'var',
        ], tkwidgets.EditableLabel | list[ttk.Entry | tk.StringVar] | ttk.Button]:
            row_size = 25
            
            label_frame = ttk.Frame(self.properties['left'])
            
            if label_editable:
                name = tkwidgets.EditableLabel(
                    label_frame,
                    text = property,
                    callback = label_callback,
                    foreground = label_color,
                )
            else:
                name = ttk.Label(
                    label_frame,
                    text = property,
                    foreground = label_color,
                )
                
            if label_prefix not in ['', None]:
                prefix = ttk.Label(
                    label_frame,
                    text = label_prefix,
                )
                prefix.pack(side = 'left')
            
            label_frame.grid(row=row, sticky='we')
            name.pack(side = 'left')
            
            if name.winfo_reqheight() > row_size:
                row_size = name.winfo_reqheight()
            
            inputs = []
            vars = []
            
            def inputType(type, value):
                if type == 'number':
                    var = tk.DoubleVar(value = value)
                    input = ttk.Spinbox(
                        self.properties['right'],
                        textvariable = var,
                        **kwargs
                    )
                else:
                    var = tk.StringVar(value = value)
                    if options and len(options) > 0:
                        input = ttk.Combobox(
                            self.properties['right'],
                            textvariable = var,
                            values = options,
                            **kwargs,
                        )
                    else:
                        input = ttk.Entry(
                            self.properties['right'],
                            textvariable = var,
                            **kwargs,
                        )
                
                # input.insert(0, value)
                
                return input, var
            
            if isinstance(type, (tuple, list)):
                column = 0
                for t in type:
                    t = t.lower()
                    input, var = inputType(t, value[column])
                    input.grid(column = column, row=row, sticky='ew', padx=2)
                    if callable(entry_callback) and update_on_entry_edit:
                        var.trace_add('write', lambda *args, value = var.get, col = column: entry_callback(value(), col))
                    
                    input.bind('<Return>', lambda e: self.focus())
                    if not update_on_entry_edit:
                        input.bind('<FocusOut>', lambda e, value = input.get, col = column: entry_callback(value(), col))
                        
                        # input.bind('<Return>', lambda e, value = input.get, col = column: entry_callback(value(), col))
                    
                    column += 1
                    
                    inputs.append(input)
                    vars.append(var)
                    
                    if input.winfo_reqheight() > row_size:
                        row_size = input.winfo_reqheight()
                    
            else:
                type = type.lower()
                
                input, var = inputType(type, value)
                input.grid(column = 0, row=row, sticky = 'ew', columnspan=2, padx=2)
                
                if entry_callback and update_on_entry_edit:
                    var.trace_add('write', lambda *args: entry_callback(var.get()))
                    # input.bind('<Return>', lambda e: entry_callback(input.get()))
                    input.bind('<FocusOut>', lambda e: entry_callback(input.get()))
                
                input.bind('<Return>', lambda e: self.focus())
                if not update_on_entry_edit:
                    input.bind('<FocusOut>', lambda e: entry_callback(input.get()))
                
                if input.winfo_reqheight() > row_size:
                    row_size = input.winfo_reqheight()
                
                inputs.append(input)
                vars.append(var)
            
            button = None
            
            if show_button:
                def callback(*args):
                    if callable(button_callback):
                        value = button_callback(vars, *args)
                        if value != None:
                            if len(vars) > 1 and isinstance(value, (list, tuple)):
                                for i, val in enumerate(value[0:len(vars)]):
                                    vars[i].set(str(val))
                            else:
                                vars[0].set(str(value))
                
                # if isinstance(button_image, Image.Image):
                #     logging.debug(f'button is PIL image: {button_image}')
                #     button_image = ImageTk.PhotoImage(button_image.resize((32,32)))
                #     button_text = None
                # else:
                #     logging.debug(f'button not PIL image: {button_image}')
                    
                
                button = crossplatform.Button(
                    self.properties['right'],
                    text = button_text,
                    width = 2,
                    command = callback,
                    bitmap = button_bitmap,
                    image = button_image,
                )
                button.grid(column = 2, row = row)
                
                if button.winfo_reqheight() > row_size:
                    row_size = button.winfo_reqheight()
            
            # row_size += 5
            
            logging.debug(f'{row_size = }')
            
            self.properties['left'].rowconfigure(row, minsize = row_size)
            self.properties['right'].rowconfigure(row, minsize = row_size)
            
            return {
                'label' : name,
                'inputs' : inputs,
                'button' : button,
                'size' : row_size,
                'var' : vars,
            }
        
        def removeProperty(property):
            if property in obj.properties:
                del obj.properties[property]
                if not isLevel:
                    self.updateObject(obj)
                    self.updateProperties(obj)
                else:
                    self.updateProperties()
    
        def updateProperty(property, value):
            obj.properties[property] = value
            if not isLevel:
                self.updateObject(obj)
        
        def resetProperty(property):
            if property in obj.defaultProperties:
                obj.properties[property] = obj.defaultProperties[property]
                
                self.updateObject(obj)
                self.updateProperties(obj)
        
        def updatePropertyName(property, newName, skip_unedited = False):
            if newName == property and not skip_unedited:
                return True
            logging.debug(f'{newName = }')
            logging.debug(f'{property = }')
            
            if newName in obj.properties:
                messagebox.showerror(
                    'Property name already exists',
                    f'Property "{newName}" already exists.'
                )
                
                return False
            else:
                value = 0
                if property in obj.properties:
                    value = obj.properties[property]
                    del obj.properties[property]
                obj.properties[newName] = value
                
                if isLevel:
                    self.updateProperties()
                else:
                    self.updateObject(obj)
                    self.updateProperties(obj)
                
                self.updateObjectSelector()
                return True
        
        def updatePosition(value, column):
            newPos = float(value)
            pos = list(obj.pos)
            
            pos[column] = newPos
            
            obj.pos = tuple(pos)
            
            self.updateObject(obj)

        def updateObjectName(name):
            obj.name = name
            self.updateObject(obj)
            self.updateObjectSelector()
        
        sizes : list[int] = []
        
        row = -1
        
        if not isLevel:
            self.objectProperties['name'] = addProperty(
                'Name',
                obj.name,
                'text',
                label_editable = False,
                show_button = False,
                entry_callback = lambda value : updateObjectName(value),
                row=0,
            )
            sizes.append(self.objectProperties['name']['size'])
            
            self.objectProperties['pos'] = addProperty(
                'Pos',
                obj.pos,
                ['number', 'number'],
                label_editable = False,
                show_button=False,
                row=1,
                entry_callback = lambda value, col : updatePosition(value, col),
                from_ = -99,
                to = 99,
            )
            sizes.append(self.objectProperties['pos']['size'])
            
            
            angle = obj.properties.setdefault('Angle', 0)
            self.objectProperties['angle'] = addProperty(
                'Angle',
                angle,
                'number',
                label_editable = False,
                show_button = False,
                row=2,
                from_=-360,
                to=360,
                entry_callback = lambda value: updateProperty('Angle', value),
            )
            sizes.append(self.objectProperties['angle']['size'])
            
            self.objectProperties['Filename'] = addProperty(
                'Filename',
                obj.filename,
                'text',
                label_editable = False,
                show_button = True,
                row = 3,
                update_on_entry_edit = False,
                entry_callback = lambda name, object = obj: self.changeObjectFilename(object, f':game:{name}'),
                button_callback = lambda vars, object = obj: self.changeObjectFilename(object, None),
                button_image = self.getAsset('folder_icon'),
            )
            sizes.append(self.objectProperties['angle']['size'])
            
            row = 4
        
        for property in obj.properties:
            if property not in ['Angle', 'Filename']:
                row += 1
                logging.debug(f'{property = }')
                prefix = ''
                button_text = '-'
                button_callback = lambda *args, prop = property : removeProperty(prop)
                color = 'black'
                
                if not isLevel and property in obj.defaultProperties:
                    prefix = '*'
                    # button_text = '↺'
                    
                    # button_callback = lambda *args, prop = property : resetProperty(prop)
                
                logging.debug(f'selectedPart: {self.selectedPart}')
                logging.debug(f'property selected: {self.selectedPart["property"] == property}')
                if self.selectedPart['property'] == property:
                    color = 'blue'
                
                options = []
                
                if not isLevel and obj.Type:
                    options_property = property
                    split_property = obj.Type.split_property_num(property)
                    if split_property[1]:
                        options_property = split_property[0] + '#'
                    
                    logging.debug(f'options_property: {options_property}')
                    
                    property_def = obj.Type.PROPERTIES.get(options_property, {})
                    logging.debug(f'property_def: {property_def}')
                    
                    property_type = property_def.get('type', 'string')
                    
                    if property_type == 'object':
                        options = [o.name for o in self.level.objects if o is not obj]
                    elif property_type == 'fluid':
                        options = []
                        for material in self.game._LEVEL_MATERIALS:
                            name = self.game._LEVEL_MATERIALS[material].get('name')
                            if isinstance(name, list):
                                options.extend(name)
                            elif name:
                                options.append(name)
                    
                    if len(options) == 0:
                        options = property_def.get('options', [])

                    logging.debug(f'options: {options}')
                
                self.objectProperties[property] = addProperty(
                    property,
                    obj.properties[property],
                    options = options,
                    row = row,
                    button_text = button_text,
                    label_editable = True,
                    entry_callback = lambda value, prop = property: updateProperty(prop, value),
                    label_callback = lambda name, prop = property: updatePropertyName(prop, name),
                    button_callback = button_callback,
                    label_prefix = prefix,
                    label_color = color,
                )
                
                sizes.append(self.objectProperties[property]['size'])
        
        if len(sizes) == 0:
            self.properties['panned'].configure(height = 1)
        else:
            self.properties['panned'].configure(height = sum(sizes))
        self.properties['scrollFrame'].resetCanvasScroll()
        
        def addNewProperty(row):
            if isLevel:
                properties = {}
            else:
                properties = deepcopy(obj.defaultProperties)
            
            if not isLevel and obj.Type:
                for prop in obj.Type.PROPERTIES:
                    property = prop
                    if prop.endswith('#'):
                        split_prop = obj.Type.split_property_num(prop)
                        num = 0
                        while split_prop[0] + str(num) in obj.properties:
                            num += 1
                        property = split_prop[0] + str(num)
                    
                    if property in properties:
                        continue
                    
                    properties[property] = obj.Type.PROPERTIES[prop].get('default', '')
            
            for prop in obj.properties:
                if prop in properties:
                    del properties[prop]
            
            property = popups.askstringoptions(
                self,
                'New property',
                'New property',
                validate_message = 'Property already exists',
                options = sorted(properties),
                validate_callback = lambda name : (name != '') and (name not in obj.properties),
            )
            
            if property != None:
                obj.properties[property] = properties.get(property, '')
                
                self.updateProperties()
        
        logging.debug(f'{row = }')
        
        add = crossplatform.Button(
            self.properties['frame'],
            text = 'Add',
            command = lambda *args,
            r = row + 1 : addNewProperty(r),
        )
        add.pack(side = 'bottom', expand = True, fill = 'x')
        
        
    def resetProperties(self):
        self.objectProperties : dict[
            str, dict[
                typing.Literal[
                    'var',
                    'label',
                    'inputs',
                    'button',
                    'size',
                ],
                tkwidgets.EditableLabel |
                ttk.Button |
                list[tk.StringVar | ttk.Entry] |
                int
            ]
        ] = {}
        
        for child in self.properties['frame'].winfo_children():
            if child != self.properties.get('panned', None):
                child.destroy()
        
        if not 'panned' in self.properties:
            self.properties['panned'] = ttk.PanedWindow(
                self.properties['frame'],
                orient='horizontal',
                style = 'Horizontal.TPanedWindow'
            )
            self.properties['panned'].pack(expand=True, fill='both')
        
        if 'left' in self.properties:
            for widget in self.properties['left'].winfo_children():
                widget.destroy()
        else:
            self.properties['left'] = ttk.Frame(self.properties['panned'])
            self.properties['panned'].add(self.properties['left'], weight=2)
            
        if 'right' in self.properties:
            for widget in self.properties['right'].winfo_children():
                widget.destroy()
        else:
            self.properties['right'] = ttk.Frame(self.properties['panned'])
            self.properties['panned'].add(self.properties['right'], weight=2)
            self.properties['right'].columnconfigure(0, weight = 2)
            self.properties['right'].columnconfigure(1, weight = 2)
            # self.properties['right'].columnconfigure(2, weight = 1)
    
    def updateObjectSelector(self):
        self.resetObjectSelector()
        
        for obj in self.level.objects:
            self.object_selector['treeview'].insert(
                '',
                'end',
                text = obj.name,
                open = True,
                values = [obj.name, obj.type if obj.type != None else '', obj.id],
                tags = 'object'
            )
            
            # self.object_selector['treeview'].item(item_id, '')
        
        def selectObject(event: tk.Event):
            if event.widget.identify_row(event.y) not in event.widget.selection():
                event.widget.selection_set(event.widget.identify_row(event.y))

            item = self.object_selector['treeview'].selection()
            # logging.debug(f"selection: {self.object_selector['treeview'].selection()}")
            item = self.object_selector['treeview'].item(item)
            self.level_canvas.focus_set()
            
            if 'object' in item['tags']:
                id = item['values'][2]
                obj = self.level.getObjectById(id)
                self.selectObject(obj)
                return obj, item

            return None, None
        
        def move_object(obj: wmwpy.classes.Object, target_index: int):
            self.level.objects.insert(target_index, self.level.objects.pop(self.level.objects.index(obj)))

            self.redrawLevel()
            self.selectObject(obj)
            
        def move_to_bottom(obj: wmwpy.classes.Object):
            current_pos = self.level.objects.index(obj)

            if current_pos == len(self.level.objects) - 1:
                return
            
            move_object(obj, len(self.level.objects) - 1)
        
        def move_down(obj: wmwpy.classes.Object):
            current_pos = self.level.objects.index(obj)

            if current_pos == len(self.level.objects) - 1:
                return
            
            move_object(obj, current_pos + 1)
        
        def move_up(obj: wmwpy.classes.Object):
            current_pos = self.level.objects.index(obj)

            if current_pos == 0:
                return
            
            move_object(obj, current_pos - 1)
        
        def move_to_top(obj: wmwpy.classes.Object):
            current_pos = self.level.objects.index(obj)

            if current_pos == 0:
                return
            
            move_object(obj, 0)
        
        def rightClick(event):
            logging.debug('object selector context menu')
            
            obj, item = selectObject(event)

            logging.debug(f'item: {item}')
            
            if obj is None:
                return

            self.object_selector['menu'].delete(0, 8)
            self.object_selector['menu'].add_command(label = '↑↑ move to top', command = lambda *args : move_to_top(obj))
            self.object_selector['menu'].add_command(label = '↑ move up', command = lambda *args : move_up(obj))
            self.object_selector['menu'].add_command(label = '↓ move down', command = lambda *args : move_down(obj))
            self.object_selector['menu'].add_command(label = '↓↓ move to bottom', command = lambda *args : move_to_bottom(obj))
            self.object_selector['menu'].add_separator()
            self.object_selector['menu'].add_command(label = 'copy', command = lambda *args : self.copyObject(obj))
            self.object_selector['menu'].add_command(label = 'cut', command = lambda *args : self.cutObject(obj))
            self.object_selector['menu'].add_command(label = 'delete', command = lambda *args : self.deleteObject(obj))
            
            self.showPopup(self.object_selector['menu'], event)
        
        self.object_selector['treeview'].bind('<ButtonRelease-1>', selectObject)

        if platform.system() == 'Darwin':
            self.object_selector['treeview'].bind('<Button-2>', rightClick)
        else:
            self.object_selector['treeview'].bind('<Button-3>', rightClick)
        
    def resetObjectSelector(self):
        
        for row in self.object_selector['treeview'].get_children():
            self.object_selector['treeview'].delete(row)

    
    def updateLevelScroll(self):
        if self.level == None:
            self.level_canvas.config(scrollregion=(0, 0, 0, 0))
            return
        
        LEVEL_CANVAS_PADDING = [200,200]
        
        level_size = numpy.array(
            (((self.level.image.size[0] / 2) * -1,
            (self.level.image.size[1] / 2) * -1),
            ((self.level.image.size[0] / 2),
            (self.level.image.size[1] / 2)))
        )
        
        objects = self.level_canvas.find_withtag('object')
        coords = numpy.array([self.level_canvas.coords(id) for id in objects])
        if len(coords) > 0:
            coords = coords.swapaxes(0,1)
        else:
            coords = numpy.array([[0],[0]])
        
        min = numpy.array([a.min() for a in coords])
        max = numpy.array([a.max() for a in coords])
        
        
        min = numpy.append(min, level_size[0]).reshape([2,2]).swapaxes(0,1)  - LEVEL_CANVAS_PADDING
        max = numpy.append(max, level_size[1]).reshape([2,2]).swapaxes(0,1)  + LEVEL_CANVAS_PADDING
        
        # logging.debug(f'{max = }')
        # logging.debug(f'{min = }')
        
        min = [a.min() for a in min]
        max = [a.max() for a in max]
        
        scrollregion = tuple(numpy.append(min,max))
        
        # logging.debug(f'scrollregion = {scrollregion}')
        
        self.level_canvas.config(scrollregion = scrollregion)
        
    
    def updateLevel(self):
        if self.level == None:
            return
        
        self.level_canvas.itemconfig(
            self.level_images['background'],
            image = self.level.PhotoImage
        )
        
        logging.info('updating level')
        
        self.selectedObject = None
        self.selectedPart = {
            'type': None,
            'id': None,
            'property': None,
        }
        self.updateProperties()
        self.updateSelectionRectangle()
        self.updateObjectSelector()
        
        for obj in self.level.objects:
            self.updateObject(obj)
        
        self.updateLevelScroll()
        self.level_canvas.xview_moveto(0.23)
        self.level_canvas.yview_moveto(0.2)
        
        self.level_canvas.tag_bind('passthrough', '<Button-1>', self.onLevelClick)
    
    def redrawLevel(self):
        self.level_canvas.delete('object')
        self.level_canvas.delete('selection')
        
        self.updateLevel()
    
    def dragObject(self, obj : wmwpy.classes.Object, event = None):
        logging.debug(f"offset: {self.dragInfo['offset']}")
        
        obj.pos = self.windowPosToWMWPos(numpy.array((event.x, event.y)) + self.dragInfo['offset'])
        
        self.updateObject(obj)
    
    def windowPosToWMWPos(self, pos : tuple = (0,0), multiplier: float = OBJECT_MULTIPLIER):
        if isinstance(pos, (int, float)):
            pos = pos / self.level.scale
            pos = pos / multiplier

            return pos
        else:
            pos = numpy.array((self.level_canvas.canvasx(pos[0]),
                            self.level_canvas.canvasy(pos[1])))
            pos = pos / self.level.scale
            pos = pos / numpy.array([multiplier, -multiplier])
            
            return tuple(pos)
    
    def getRelativeMousePos(self, pos : tuple, widget : tk.Widget):
        return numpy.array((numpy.array(pos) - (self.winfo_rootx(),
                             self.winfo_rooty())) - (widget.winfo_x(),
                                                     widget.winfo_y()))
    
    def selectObject(
        self,
        obj : wmwpy.classes.Object = None,
        event: tk.Event | None = None,
        partInfo: dict[str, str] = None,
    ):
        self.selectedPart = {
            'type': None,
            'id': None,
            'property': None,
        }
        old_object = self.selectedObject
        self.selectedObject = obj
        if old_object in self.level.objects:
            self.updateObject(old_object)
        
        if isinstance(partInfo, dict):
            self.selectedPart['type'] = partInfo.get('type', None)
            self.selectedPart['id'] = partInfo.get('id', None)
            self.selectedPart['property'] = partInfo.get('property', None)
        
        
        # logging.debug(obj.name)
        logging.debug('object')
        
        self.updateObject(obj)
        self.updateProperties()
        self.updateSelectionRectangle()
        if event:
            obj_pos = self.getObjectPosition(obj.pos, obj.offset)
            self.dragInfo['offset'] = numpy.array((obj_pos[0], obj_pos[1])) - (self.level_canvas.canvasx(event.x), self.level_canvas.canvasy(event.y))
        else:
            self.dragInfo['offset'] = (0,0)
        
        if self.selectedObject == None:
            if len(self.object_selector['treeview'].selection()) > 0:
                self.object_selector['treeview'].selection_remove(self.object_selector['treeview'].selection()[0])
        else:
            
            children = self.object_selector['treeview'].get_children('')
            
            selected = None
            
            for child in children:
                item = self.object_selector['treeview'].item(child)
                
                if not 'object' in item['tags']:
                    logging.info('not object')
                    continue
                
                if item['values'][2] == obj.id:
                    selected = child
                    break
            
            if selected != None:
                self.object_selector['treeview'].selection_set(selected)
    
    def selectPart(
        self,
        obj: wmwpy.classes.Object,
        type: str,
        id: str,
        property: str,
    ):
        self.selectObject(
            obj,
            partInfo = {
                'type': type,
                'id': id,
                'property': property,
            }
        )
        logging.debug(f'selected part: {self.selectedPart}')
        return self.selectedPart
    
    def dragPart(
        self,
        event: tk.Event = None,
        obj: wmwpy.classes.Object | None = None,
        amount: tuple[float, float] | None = None,
    ):
        if obj == None:
            obj = self.selectedObject
        if obj == None:
            return

        logging.debug('dragging part')
        if self.selectedPart['type'] == 'path':
            logging.debug('type: path')
            is_global = False
            if obj.Type and obj.Type.get_property('PathIsGlobal'):
                is_global = True
            
            if amount:
                current = obj.Type.get_property(self.selectedPart['property'])
                pos = numpy.array(current) + amount
            else:
                pos = self.windowPosToWMWPos((event.x, event.y), (0.25 * is_global) + 1)
            
                if not is_global:
                    pos = numpy.array(pos) - (numpy.array(obj.pos) * 1.25)
            
            logging.debug(f'new pos: {pos}')
            obj.properties[self.selectedPart['property']] = ' '.join([str(x) for x in pos])
            self.objectProperties[self.selectedPart['property']]['var'][0].set(obj.properties[self.selectedPart['property']])
        
        self.updateObject(obj)
    
    def createMenubar(self):
        self.menubar = tk.Menu(self)
        self.config(menu = self.menubar)
        
        self.file_menu = tk.Menu(self.menubar, tearoff = 0)
        
        self.file_menu.add_command(label = 'Open', command = self.openLevel, accelerator = f'{crossplatform.shortModifier()}+O')
        self.file_menu.add_command(label = 'Save', command = self.saveLevel, accelerator = f'{crossplatform.shortModifier()}+S')
        self.file_menu.add_command(label = 'Save as...', command = self.saveLevelAs, accelerator = f'{crossplatform.shortModifier()}+Shift+S')
        self.file_menu.add_separator()
        self.file_menu.add_command(label = 'Settings', command = self.showSettings)


        self.help_menu = tk.Menu(self.menubar, tearoff = 0)

        self.help_menu.add_command(label = 'Discord', command = lambda *args : webbrowser.open(__links__['discord']))
        self.help_menu.add_command(label = 'About', command = self.showAbout)
        self.help_menu.add_command(label = 'Check for update', command = lambda *args : webbrowser.open(__links__['releases']))
        self.help_menu.add_command(label = 'Bug report', command = lambda *args : webbrowser.open(__links__['bugs']))
        self.help_menu.add_command(label = 'Open log', command = lambda *args : crossplatform.open_file(_log_filename))


        self.view_menu: dict[
            typing.Literal[
                'menu',
                'sub',
                'vars',
            ],
            tk.Menu | dict[typing.Literal[
                'radius',
                'PlatinumType',
            ], tk.BooleanVar] | dict[str, tk.Menu]
        ] = {
            'menu': tk.Menu(self.menubar, tearoff = 0),
            'sub': {
                'PlatinumType': None,
            },
            'vars': {
                'radius': tk.BooleanVar(value = self.settings.get('view.radius', True)),
                'PlatinumType': {
                    'platinum': tk.BooleanVar(value = self.settings.get('view.PlatinumType.platinum', True)),
                    'normal': tk.BooleanVar(value = self.settings.get('view.PlatinumType.normal', True)),
                    'note': tk.BooleanVar(value = self.settings.get('view.PlatinumType.note', True)),
                    'none': tk.BooleanVar(value = self.settings.get('view.PlatinumType.none', True)),
                },
                'path': tk.BooleanVar(value = self.settings.get('view.radius', True)),
            }
        }
        
        self.view_menu['vars']['radius'].trace_add('write', lambda *args : self.updateView('radius', self.view_menu['vars']['radius'].get()))
        self.view_menu['menu'].add_checkbutton(label = 'radius', onvalue = True, offvalue = False, variable = self.view_menu['vars']['radius'])

        self.view_menu['sub']['PlatinumType'] = tk.Menu(self.view_menu['menu'], tearoff = 0)
        
        self.view_menu['vars']['PlatinumType']['platinum'].trace_add('write', lambda *args : self.updateView('PlatinumType.platinum', self.view_menu['vars']['PlatinumType']['platinum'].get()))
        self.view_menu['sub']['PlatinumType'].add_checkbutton(label = 'platinum', onvalue = True, offvalue = False, variable = self.view_menu['vars']['PlatinumType']['platinum'])
        self.view_menu['vars']['PlatinumType']['normal'].trace_add('write', lambda *args : self.updateView('PlatinumType.normal', self.view_menu['vars']['PlatinumType']['normal'].get()))
        self.view_menu['sub']['PlatinumType'].add_checkbutton(label = 'normal', onvalue = True, offvalue = False, variable = self.view_menu['vars']['PlatinumType']['normal'])
        self.view_menu['vars']['PlatinumType']['note'].trace_add('write', lambda *args : self.updateView('PlatinumType.note', self.view_menu['vars']['PlatinumType']['note'].get()))
        self.view_menu['sub']['PlatinumType'].add_checkbutton(label = 'note', onvalue = True, offvalue = False, variable = self.view_menu['vars']['PlatinumType']['note'])
        self.view_menu['vars']['PlatinumType']['none'].trace_add('write', lambda *args : self.updateView('PlatinumType.none', self.view_menu['vars']['PlatinumType']['none'].get()))
        self.view_menu['sub']['PlatinumType'].add_checkbutton(label = 'none', onvalue = True, offvalue = False, variable = self.view_menu['vars']['PlatinumType']['none'])

        self.view_menu['menu'].add_cascade(label = 'platinum type', menu = self.view_menu['sub']['PlatinumType'])
        
        self.view_menu['vars']['path'].trace_add('write', lambda *args : self.updateView('path', self.view_menu['vars']['path'].get()))
        self.view_menu['menu'].add_checkbutton(label = 'path', onvalue = True, offvalue = False, variable = self.view_menu['vars']['path'])

        self.menubar.add_cascade(label = 'File', menu = self.file_menu)
        self.menubar.add_cascade(label = 'View', menu = self.view_menu['menu'])
        self.menubar.add_cascade(label = 'Help', menu = self.help_menu)
    
    def updateView(self, view: str, state: bool = True):
        self.settings.set(['view', view], state)
        self.updateLevel()
    
    def showAbout(self):
        about = popups.About(
            self,
            title = "About",
            author = __author__,
            program = "Where's My Editor?",
            version = f'{__version__}\nwmwpy-{wmwpy.__version__}',
            description = """Where's My Editor? is a program to create and modify levels in the Where's My Water? game series.""",
            credits = __credits__,
            logo = Image.open(self.getAssetPath(self.LOGO)),
        )
    
    def showSettings(self):
        settings = popups.SettingsDialog(
            self,
            self.settings,
        )
    
    def openLevel(self, *args):
        xml = filedialog.askopenfilename(
            defaultextension = '.xml',
            filetypes = (
                ('WMW Level', '.xml'),
                ('Any', '*.*')
            ),
            initialdir = wmwpy.utils.path.joinPath(
                self.game.gamepath,
                self.game.assets,
                self.game.baseassets,
                'Levels'
            )
        )
        
        if xml in ['', None]:
            logging.debug('Open level canceled')
            return
        
        image = os.path.splitext(xml)[0] + '.png'
        
        self.loadLevel(xml, image)
    
    def saveLevel(self, *args, filename = None):
        if not isinstance(self.level, wmwpy.classes.Level):
            self.updateProgressBar(
                1,
                'No level to be saved.',
                1,
            )
            return
        xml = self.level.export(
            filename = filename,
            saveImage = True,
        )
        
        if filename == None:
            filename = wmwpy.utils.path.joinPath(
                self.game.gamepath,
                self.game.assets,
                self.game.baseassets,
                self.level.filename,
            )
        
        imagePath = os.path.splitext(filename)[0] + '.png'
        
        try:
            self.level.image.save(imagePath)
        except:
            logging.exception('failed to save level image')
        
        try:
            with open(filename, 'wb') as file:
                file.write(xml)
            
            self.level._image.save(os.path.splitext(filename)[0] + '.png')
            
            self.updateProgressBar(
                1,
                f'Successfully saved level',
                1,
            )
        except:
            messagebox.showerror('Error saving level', f'Unable to save level to {filename}')
        
    
    def saveLevelAs(self, *args):
        if not isinstance(self.level, wmwpy.classes.Level):
            self.updateProgressBar(
                1,
                'No level to be saved.',
                1,
            )
            return
        
        filename = filedialog.asksaveasfilename(
            initialfile = os.path.basename(self.level.filename),
            defaultextension = '.xml',
            filetypes = (
                ('WMW Level', '.xml'),
                ('Any', '*.*')
            ),
            initialdir = wmwpy.utils.path.joinPath(
                self.game.gamepath,
                self.game.assets,
                self.game.baseassets,
                'Levels'
            ),
        )
        
        if filename in ['', None]:
            return
        
        self.saveLevel(filename = filename)
    
    def getFile(self, path : str):
        logging.debug(f'getFile: path: {path}')
        if not isinstance(path, str):
            raise TypeError('path must be str')
        
        if path in ['', None]:
            logging.debug('getFile: no path')
            return
        
        if path.startswith(':game:'):
            logging.debug(f'getFile: path starts with :game:')
            path = path.partition(':game:')[-1]
            
            path = pathlib.Path('/', path).as_posix()
            
            logging.debug(f'getFile: path after :game: {path}')
            
            file = self.game.filesystem.get(path)
            if isinstance(file, wmwpy.filesystem.File):
                file.reload()
            return file
        
        path = pathlib.PurePath(path)
        assets = wmwpy.utils.path.joinPath(
            self.game.gamepath,
            self.game.assets,
        )
        
        print(f'getFile: In filesystem? {path.is_relative_to(assets)}')
        if path.is_relative_to(assets):
            logging.debug(f'getFile: relative path')
            relPath = os.path.relpath(path, assets)
            relPath = pathlib.Path('/', relPath).as_posix()
            logging.debug(f'getFile: rel path: {relPath}')
            file = self.game.filesystem.get(relPath)
            
            logging.debug(f'getFile: game.filesystem: {self.game.filesystem}')
            logging.debug(f'getFile: game.filesystem.root: {self.game.filesystem.root.path}')
            
            logging.debug(f'getFile: file: {file}')
            if isinstance(file, wmwpy.filesystem.File):
                logging.debug(f'getFile: file.path: {file.path}')
                file.reload()
            return file
        
        if path in ['', None]:
            logging.debug('getFile: no path')
            return None
        else:
            logging.debug(f'getFile: absolute path: {path}')
            file = wmwpy.filesystem.File(None, os.path.basename(path), path)
        
        return file
    
    def loadGame(self):
        gamepath = self.settings.get('game.gamepath')
        logging.debug(f'gamepath: {gamepath}')
        if not gamepath:
            gamepath = filedialog.askdirectory(
                parent = self,
                title = 'Select Game directory',
                mustexist = True,
            )
            self.settings.set('game.gamepath', gamepath)
        
        self.state = 'disabled'
        
        try:
            self.game = wmwpy.load(
                self.settings.get('game.gamepath'),
                assets = self.settings.get('game.assets'),
                game = self.settings.get('game.game'),
                load_callback = self.updateProgressBar,
            )
        except:
            logging.exception(f'unable to load game: {self.settings.get("game.gamepath")}')
        
        self.state = 'enabled'
    
    def loadLevel(self, xml : str, image : str):
        if self.game in ['', None]:
            logging.warning('no game is loaded')
            return
        
        if (xml in ['', None]) and (image in ['', None]):
            logging.warning('No level to load')
            return
        
        self.state = 'disabled'
        
        logging.debug(f'{xml = }')
        logging.debug(f'{image = }')
        
        xml = self.getFile(xml)
        image = self.getFile(image)
        
        logging.debug(f'loadLevel: xml: {xml}')
        logging.debug(f'loadLevel: image: {image}')
        
        if isinstance(self.level, wmwpy.classes.Level):
            self.level_canvas.delete('object')
            self.level_canvas.delete('part')
            self.level_canvas.delete('selection')
            self.level.objects.clear()
        
        self.resetProperties()
        self.resetObjectSelector()
        
        try:
            logging.debug(f'loading level:')
            logging.debug(f'xml: {xml}')
            logging.debug(f'image: {image}')
            self.level = self.game.Level(
                xml,
                image,
                HD = True,
                TabHD = True,
                ignore_errors = True,
                load_callback = self.updateProgressBar,
            )
        except:
            logging.exception('Unable to load level')
            self.state = 'enabled'
            return
        
        logging.debug(f'level = {self.level}')
        logging.debug(f'objects = {self.level.objects}')
        
        self.level.scale = 5
        self.updateLevel()
        logging.info('finished loading level')
        self.state = 'enabled'
        
        self.title(f"Where's My Editor - {os.path.splitext(os.path.basename(self.level.filename))[0]}")
        
        return self.level
    
    def close(self):
        result = False
        if self.level != None:
            result = messagebox.askyesnocancel(
                'Unsaved changes',
                message = 'Do you want to save changes?',
            )
        
        logging.debug(f'close option: {result}')
        
        if result:
            self.saveLevelAs()
        
        if result != None:
            self.destroy()
    
    def updateSettings(self):
        try:
            gamedir = self.settings.get('gamedir')
            if gamedir:
                self.settings.set('game.gamepath', gamedir)
                self.settings.remove('gamedir')
        except:
            pass
        try:
            default_level = self.settings.get('default_level')
            if default_level:
                self.settings.set('game.default_level', default_level)
                self.settings.remove('default_level')
        except:
            pass



class TkErrorCatcher:

    '''
    In some cases tkinter will only print the traceback.
    Enables the program to catch tkinter errors and log them.

    To use
    import tkinter
    tkinter.CallWrapper = TkErrorCatcher
    '''

    def __init__(self, func, subst, widget):
        self.func = func
        self.subst = subst
        self.widget = widget

    def __call__(self, *args):
        try:
            if self.subst:
                args = self.subst(*args)
            return self.func(*args)
        except SystemExit as msg:
            raise SystemExit(msg)
        except Exception as e:
            logging.exception('tk error')

tk.CallWrapper = TkErrorCatcher

def main():
    try:
        app = WME(None)
        app.mainloop()
    except Exception as e:
        logging.exception('WME ended prematurely')

if(__name__ == '__main__'):
    main()
