__version__ = '2.2.0'
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
}

__wmwpy_version__ = "0.3.0-beta"

import traceback
import logging
import os
import sys
import io
import platform
from datetime import datetime

def createLogger(type = 'file', filename = 'logs/log.log'):
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    format = '[%(levelname)s] %(message)s'
    datefmt = '%I:%M:%S %p'
    level = logging.DEBUG

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


_log_filename = f'logs/{datetime.now().strftime("%m-%d-%y_%H-%M-%S")}.log'

createLogger('file', filename = _log_filename)

def log_exception():
    fileio = io.StringIO()
    traceback.print_exc(file = fileio)
    
    logging.error(fileio.getvalue())

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
import tkwidgets
from PIL import Image, ImageTk, ImageColor, ImageDraw
import json
from settings import Settings
from lxml import etree
import numpy
import typing
from copy import copy
import pathlib
import webbrowser

import wmwpy
from scrollframe import ScrollFrame
import popups

if wmwpy.__version__ < __wmwpy_version__:
    logging.error(f'wmwpy version must be "{__wmwpy_version__}" or higher.')
    raise ImportWarning(f'wmwpy version must be "{__wmwpy_version__}" or higher.')

ImageColor.colormap['transparent'] = '#0000'

class WME(tk.Tk):
    APP_ICONS = [
            'assets/images/icon_256x256.ico',
        ]
    LOGO = 'assets/images/WME_logo.png'
    
    def __init__(self, parent):
        tk.Tk.__init__(self,parent)
        self.parent = parent
        
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            self.WME_assets = sys._MEIPASS
        else:
            self.WME_assets = '.'
        
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
            }
        )
        self.updateSettings()

        self.selection_rect = None

        self.style = ttk.Style()

        self.active = True

        self.selectedObject = None
        self.level : wmwpy.classes.Level = None
        self.game : wmwpy.Game = None
        
        self.createMenubar()
        self.createWindow()
        
        self.loadGame()
        
        if self.game != None:
            self.loadLevel(
                self.settings.get('game.default_level.xml'),
                self.settings.get('game.default_level.image')
            )
    
    def getAsset(self, path : str):
        return os.path.join(self.WME_assets, path)
    
    def findIcons(self):
        self.windowIcons : dict[str, ImageTk.PhotoImage] = {}
        
        for icon in self.APP_ICONS:
            try:
                self.windowIcons[self.getAsset(icon)] = ImageTk.PhotoImage(
                        Image.open(self.getAsset(icon))
                    )
                
            except:
                pass
        
        return self.windowIcons

    def createWindow(self):
        self.seperator = ttk.PanedWindow(orient='horizontal')
        self.seperator.pack(fill=tk.BOTH, expand=1)

        self.side_pane = ttk.PanedWindow(self.seperator, orient='vertical')
        self.seperator.add(self.side_pane)
        
        side_pane_width = 250
        side_pane_height = 300
        
        
        # create object selector
        
        self.object_selector : dict[typing.Literal[
            'labelFrame',
            'treeviewe',
            'y_scroll',
            'x_scroll',
        ], tk.Widget | ttk.Treeview] = {
            'labelFrame' : ttk.LabelFrame(self.side_pane, width=side_pane_width, height=side_pane_height, text='Objects'),
            'treeview' : None,
            'y_scroll' : None,
            'x_scroll' : None,
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
        ], tk.Widget] = {
            'labelFrame' : ttk.LabelFrame(self.side_pane, width=side_pane_width, height=side_pane_height, text='Properties')
        }
        self.side_pane.add(self.properties['labelFrame'])
        
        # self.properties['notebook'] = ttk.Notebook(self.properties['labelFrame'])
        
        self.properties['scrollFrame'] = ScrollFrame(self.properties['labelFrame'], usettk=True, width=side_pane_width,)
        # self.properties['notebook'].pack(fill='both', expand=True)
        # self.properties['notebook'].add(self.properties['scrollFrame'], text='Object Properties')
        # self.properties['notebook'].add(ttk.Frame(self.properties['notebook']), text='Level Properties')
        self.properties['scrollFrame'].pack(fill='both', expand=True)
        self.properties['frame'] = self.properties['scrollFrame'].viewPort

        self.level_canvas = tk.Canvas(self.seperator, width=90*self.scale, height=120*self.scale)
        self.seperator.add(self.level_canvas, weight=1)
        
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
    
    def bindWindowWidgets(self):
        
        if platform.system() == 'Linux':
            self.level_canvas.bind("<Button-4>", self.onLevelMouseWheel)
            self.level_canvas.bind("<Button-5>", self.onLevelMouseWheel)
            
            self.level_canvas.bind("<Shift-Button-4>", lambda *args: self.onLevelMouseWheel(*args, type = 1))
            self.level_canvas.bind("<Shift-Button-5>", lambda *args: self.onLevelMouseWheel(*args, type = 1))
        else:
            self.level_canvas.bind("<MouseWheel>", self.onLevelMouseWheel)
            self.level_canvas.bind("<Shift-MouseWheel>", lambda *args: self.onLevelMouseWheel(*args, type = 1))
        
        self.level_canvas.bind('<Button-1>', self.onLevelClick)
        self.level_canvas.bind('<Button-3>', self.onLevelRightClick)
        
        self.object_selector['treeview'].configure(selectmode = 'browse')
        self.object_selector['treeview'].state(("!disabled",))
        # re-enable item opening on click
        self.object_selector['treeview'].unbind('<Button-1>')
        
        self.updateLevel()
    
    def unbindWindowWidgets(self):
        if platform.system() == 'Linux':
            self.level_canvas.unbind("<Button-4>")
            self.level_canvas.unbind("<Button-5>")
            
            self.level_canvas.unbind("<Shift-Button-4>")
            self.level_canvas.unbind("<Shift-Button-5>")
        else:
            self.level_canvas.unbind("<MouseWheel>")
            self.level_canvas.unbind("<Shift-MouseWheel>")
            
        self.level_canvas.unbind('<Button-1>')
        self.level_canvas.unbind('<Button-3>')
        
        objects = self.level_canvas.find_withtag('object')
        objects = list(objects) + list(self.level_canvas.find_withtag('selection'))
        
        for id in objects:
            self.unbindObject(id)
        
        self.object_selector['treeview'].configure(selectmode = 'none')
        
        self.object_selector['treeview'].state(("disabled",))
        # disable item opening on click
        self.object_selector['treeview'].bind('<Button-1>', lambda e: 'break')
    
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
            raise ValueError(f'uknown state {state}')
        
        self._state = state

        if self._state == 'normal':
            self.bindWindowWidgets()
        elif self._state == 'disabled':
            self.unbindWindowWidgets()
    
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
    
    OBJECT_MULTIPLIER = [1.25,-1.25]
    
    def updateLayers(self):
        objects = self.level_canvas.find_withtag('object')
        if len(objects) < 0:
            return
        
        self.level_canvas.tag_raise('object', 'level')
        
        background = self.level_canvas.find_withtag('background')
        foreground = self.level_canvas.find_withtag('foreground')
        if len(background) > 0:
            background = 'background'
        else:
            background = 'level'
        
        if len(foreground) > 0:
            foreground = 'foreground'
        else:
            return
        
        self.level_canvas.tag_raise(foreground, background)
        
        if len(self.level_canvas.find_withtag('selection')) > 0:
            self.level_canvas.tag_raise('selection', 'object')
    
    SELECTION_BORDER_WIDTH = 2
    
    def updateSelectionRectangle(self, obj : wmwpy.classes.Object = None):
        if obj == None:
            obj = self.selectedObject
        if obj == None:
            self.level_canvas.delete('selection')
            # logging.info('deleted selection')
            return
        
        pos = numpy.array(obj.pos)
        size = numpy.array(obj.size)
        
        selectionImage = Image.new('RGBA', tuple(size * obj.scale), 'black')
        selectionImageDraw = ImageDraw.Draw(selectionImage)
        selectionImageDraw.rectangle(
            (0,0) + tuple(numpy.array(selectionImage.size) - (self.SELECTION_BORDER_WIDTH - 1)),
            fill='transparent',
            outline='black',
            width=self.SELECTION_BORDER_WIDTH,
        )
        selectionImage = obj.rotateImage(selectionImage)
        self.selectionPhotoImage = ImageTk.PhotoImage(selectionImage)
        
        pos = self.getObjectPosition(pos, obj.offset)
        
        id = self.level_canvas.find_withtag('selection')
        if len(id) <= 0:
            self.level_canvas.create_image(
                *pos,
                image = self.selectionPhotoImage,
                tags = 'selection')
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
        pos = (pos * self.OBJECT_MULTIPLIER) * self.level.scale
        
        return pos
    
    def updateObject(self, obj : wmwpy.classes.Object):
        if obj == None:
            self.updateSelectionRectangle()
            self.updateLevelScroll()
            return
        
        logging.info(f'updating object: {obj.name}, {obj.type}')
        
        offset = numpy.array(obj.offset)
        
        pos = numpy.array(obj.pos)
        
        pos = self.getObjectPosition(pos, offset)
        
        id = f'{obj.name}-{str(obj.id)}'
        
        items = self.level_canvas.find_withtag(id)
        
        background = None
        foreground = None
        
        for item in items:
            tags = self.level_canvas.gettags(item)
            if 'background' in tags:
                background = item
            elif 'foreground' in tags:
                foreground = item
        
        if len(items) > 0:
            if background:
                self.level_canvas.coords(
                    background,
                    pos[0],
                    pos[1],
                )
                self.level_canvas.itemconfig(
                    background,
                    image = obj.background_PhotoImage,
                )
            
            if foreground:
                self.level_canvas.coords(
                    foreground,
                    pos[0],
                    pos[1],
                )
                self.level_canvas.itemconfig(
                    foreground,
                    image = obj.foreground_PhotoImage,
                )
        else:
            if len(obj._background) > 0:
                self.level_canvas.create_image(
                    pos[0],
                    pos[1],
                    anchor = 'c',
                    image = obj.background_PhotoImage,
                    tags = ('object', 'background', id)
                )
                
            if len(obj._foreground) > 0:
                self.level_canvas.create_image(
                    pos[0],
                    pos[1],
                    anchor = 'c',
                    image = obj.foreground_PhotoImage,
                    tags = ('object', 'foreground', id)
                )
        
        logging.info(f"id: {id}")
        # logging.info(f"pos: {pos}\n")
        
        self.updateLayers()
        
        self.bindObject(id, obj)
        
        self.updateSelectionRectangle()
        self.updateLevelScroll()
    
    def onLevelClick(self, event : tk.Event):
        logging.info('level')
        
        mouse = (self.level_canvas.canvasx(event.x), self.level_canvas.canvasy(event.y))
        
        objects = self.level_canvas.find_overlapping(*mouse, *mouse)
        logging.info(objects)
        length = len(objects)
        
        if length <= 1:
            if length == 1:
                if objects[0] != self.level_images['background']:
                    return
            
            self.selectObject(None)
    
    def createLevelContextMenu(self):
        self.levelContextMenu = tk.Menu(self.level_canvas, tearoff = 0)
        self.levelContextMenu.add_command(label = 'add object', command = lambda *args: self.addObjectSelector(self.getRelativeMousePos(self.level_canvas.winfo_pointerxy(), self.level_canvas)))
        self.levelContextMenu.add_command(label = 'paste', state = 'disabled')
    
    def onLevelRightClick(self, event):
        logging.info('level context menu')
        logging.info(f'canvas mouse pos = {(numpy.array(self.level_canvas.winfo_pointerxy()) - (self.winfo_rootx(), self.winfo_rooty())) - (self.level_canvas.winfo_x(), self.level_canvas.winfo_y())}')
        logging.info(f'canvas mouse x = {self.winfo_pointerx() - self.winfo_rootx()}')
        logging.info(f'canvas mouse y = {self.winfo_pointery() - self.winfo_rooty()}')
        logging.info(f'event pos = {(event.x, event.y)}')
        logging.info(f'canvas pos = {(self.level_canvas.winfo_x(), self.level_canvas.winfo_y())}')
        
        mouse = (self.level_canvas.canvasx(event.x), self.level_canvas.canvasy(event.y))
        
        objects = self.level_canvas.find_overlapping(*mouse, *mouse)
        logging.info(objects)
        length = len(objects)
        
        if length <= 1:
            if length == 1:
                if objects[0] != self.level_images['background']:
                    return
            
            self.selectObject(None)
            self.showPopup(self.levelContextMenu, event)
    
    def bindObject(self, id, obj : wmwpy.classes.Object = None):
        if obj == None:
            if self.selectedObject != None:
                obj = self.selectedObject
            else:
                return
        
        self.level_canvas.tag_bind(
            id,
            '<Button1-Motion>',
            lambda e, object = obj: self.dragObject(object, e)
        )
        self.level_canvas.tag_bind(
            id,
            '<Button-1>',
            lambda e, object = obj: self.selectObject(object)
        )
        self.level_canvas.tag_bind(
            id,
            '<Button-3>',
            lambda e, object = obj, menu = self.createObjectContextMenu(obj): self.showPopup(menu, e, callback = lambda : self.selectObject(object))
        )
    
    def unbindObject(self, id):
        self.level_canvas.tag_unbind(
            id,
            '<Button1-Motion>',
        )
        self.level_canvas.tag_unbind(
            id,
            '<Button-1>',
        )
        self.level_canvas.tag_unbind(
            id,
            '<Button-3>',
        )
        
    def createObjectContextMenu(self, obj : wmwpy.classes.Object):
        menu = tk.Menu(self.level_canvas, tearoff = 0)
        menu.add_command(label = 'delete', command = lambda *args : self.deleteObject(obj))
        menu.add_command(label = 'copy', state = 'disabled')
        menu.add_command(label = 'cut', state = 'disabled')
        
        return menu
    
    def showPopup(self, menu : tk.Menu, event : tk.Event = None, callback : typing.Callable = None):
        try:
            if callback != None:
                callback()
            menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            menu.grab_release()
    
    def deleteObject(self, obj : wmwpy.classes.Object):
        self.level_canvas.delete(f'{obj.name}-{str(obj.id)}')
        
        if obj in self.level.objects:
            index = self.level.objects.index(obj)
            del self.level.objects[index]
        
        if obj == self.selectedObject:
            self.selectObject(None)
        
        self.updateObjectSelector()
    
    def addObject(
        self, obj : wmwpy.classes.Object | str,
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
    
    def addObjectSelector(self, pos : tuple = (0,0)):
        filename = filedialog.askopenfilename(
            defaultextension = '.hs',
            filetypes = (
                ('WMW Object', '*.hs'),
                ('Any', '*.*'),
            ),
            initialdir = wmwpy.Utils.path.joinPath(
                self.game.gamepath,
                self.game.assets,
                self.game.baseassets,
                'Objects'
            ),
        )
        
        logging.info(f'{pos = }')
        self.addObject(
            filename,
            pos = self.windowPosToWMWPos(pos)
        )
    
    def updateProperties(self, obj : wmwpy.classes.Object = None):
        if obj == None:
            obj = self.selectedObject
        
        self.resetProperties()
        
        if obj == None:
            self.properties['panned'].configure(height = 1)
            self.properties['scrollFrame'].resetCanvasScroll()
            return
        
        def addProperty(
            property : str,
            value : str,
            type : typing.Literal['number', 'text'] = 'text',
            show_button = True,
            row = 0,
            label_prefix : str = '',
            label_editable : bool = True,
            entry_callback : typing.Callable[[str], typing.Any] = None,
            label_callback : typing.Callable[[str], bool] = None,
            button_callback : typing.Callable = None,
            button_text : str = '-',
            **kwargs,
        ) -> dict[typing.Literal[
            'label',
            'inputs',
            'button',
            'size',
            ], tkwidgets.EditableLabel | list[ttk.Entry] | ttk.Button]:
            row_size = 25
            
            label_frame = ttk.Frame(self.properties['left'])
            
            if label_editable:
                name = tkwidgets.EditableLabel(
                    label_frame,
                    text = property,
                    callback = label_callback,
                )
            else:
                name = ttk.Label(
                    label_frame,
                    text = property,
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
            
            def inputType(type, value):
                
                if type == 'number':
                    input = ttk.Spinbox(
                        self.properties['right'],
                        **kwargs
                    )
                else:
                    input = ttk.Entry(
                        self.properties['right'],
                        **kwargs
                    )
                
                input.insert(0, value)
                
                return input
            
            if isinstance(type, (tuple, list)):
                column = 0
                for t in type:
                    t = t.lower()
                    input = inputType(t, value[column])
                    input.grid(column = column, row=row, sticky='ew')
                    if entry_callback:
                        input.bind('<Return>', lambda e, value = input.get, col = column: entry_callback(value(), col))
                        input.bind('<FocusOut>', lambda e, value = input.get, col = column: entry_callback(value(), col))
                    
                    column += 1
                    
                    inputs.append(input)
                    
                    if input.winfo_reqheight() > row_size:
                        row_size = input.winfo_reqheight()
                    
            else:
                type = type.lower()
                
                input = inputType(type, value)
                input.grid(column = 0, row=row, sticky = 'ew', columnspan=2)
                
                if entry_callback:
                    input.bind('<Return>', lambda e: entry_callback(input.get()))
                    input.bind('<FocusOut>', lambda e: entry_callback(input.get()))
                
                if input.winfo_reqheight() > row_size:
                        row_size = input.winfo_reqheight()
                
                inputs.append(input)
            
            button = None
            
            if show_button:
                button = ttk.Button(
                    self.properties['right'],
                    text=button_text,
                    width=2,
                    command = button_callback
                )
                button.grid(column=2, row=row)
                
                if button.winfo_reqheight() > row_size:
                    row_size = button.winfo_reqheight()
            
            # row_size += 5
            
            logging.debug(f'{row_size = }')
            
            self.properties['left'].rowconfigure(row, minsize=row_size)
            self.properties['right'].rowconfigure(row, minsize=row_size)
            
            return {
                'label' : name,
                'inputs' : inputs,
                'button' : button,
                'size' : row_size
            }
        
        def removePropety(property):
            if property in obj.properties:
                del obj.properties[property]
                self.updateObject(obj)
                self.updateProperties(obj)
    
        def updateProperty(property, value):
            obj.properties[property] = value
            self.updateObject(obj)
        
        def resetProperty(property):
            if property in obj.defaultProperties:
                obj.properties[property] = obj.defaultProperties[property]
                
                self.updateObject(obj)
                self.updateProperties(obj)
        
        def updatePropertyName(property, newName, skip_unedited = False):
            if newName == property and not skip_unedited:
                return True
            logging.info(f'{newName = }')
            logging.info(f'{property = }')
            
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
                
                self.updateObject(obj)
                self.updateProperties(obj)
                self.updateObjectSelector()
                
                return True
        
        def updatePosition(value, column):
            newPos = float(value)
            pos = list(obj.pos)
            
            pos[column] = newPos
            
            obj.pos = tuple(pos)
            
            logging.info(newPos)
            logging.info(pos)
            logging.info(obj.pos)
            
            self.updateObject(obj)
        
        sizes : list[int] = []
        
        sizes.append(addProperty(
            'Name',
            obj.name,
            'text',
            label_editable = False,
            show_button = False,
            row=0,
        )['size'])
        
        sizes.append(addProperty(
            'Pos',
            obj.pos,
            ['number', 'number'],
            label_editable = False,
            show_button=False,
            row=1,
            entry_callback = lambda value, col : updatePosition(value, col),
            from_ = -99,
            to = 99,
        )['size'])
        
        angle = '0'
        if 'Angle' in obj.properties:
            angle = obj.properties['Angle']
        sizes.append(addProperty(
            'Angle',
            angle,
            'number',
            label_editable = False,
            show_button = False,
            row=2,
            from_=-360,
            to=360,
            entry_callback = lambda value: updateProperty('Angle', value),
        )['size'])
        
        row = 3
        
        for property in obj.properties:
            if property not in ['Angle']:
                row += 1
                logging.debug(f'{property = }')
                prefix = ''
                button_text = '-'
                button_callback = lambda *args, prop = property : removePropety(prop)
                
                if property in obj.defaultProperties:
                    prefix = '*'
                    button_text = '↺'
                    
                    button_callback = lambda *args, prop = property : resetProperty(prop)
                
                
                sizes.append(addProperty(
                    property,
                    obj.properties[property],
                    row = row,
                    button_text = button_text,
                    label_editable = property not in obj.defaultProperties,
                    entry_callback = lambda value, prop = property: updateProperty(prop, value),
                    label_callback = lambda name, prop = property: updatePropertyName(prop, name),
                    button_callback = button_callback,
                    label_prefix = prefix,
                )['size'])
        
        self.properties['panned'].configure(height = sum(sizes))
        self.properties['scrollFrame'].resetCanvasScroll()
        
        def addNewProperty(property, value, row):
            def setProperty(name, value):
                if name in obj.properties:
                    messagebox.showerror(
                        'Property name already exists',
                        f'Property "{name}" already exists.'
                    )
                    
                    return False
                else:
                    obj.properties[name] = value
                    
                    self.updateObject(obj)
                    self.updateProperties(obj)
                    self.updateObjectSelector()
                    
                    return True
            
            logging.debug(f'adding property {property}')
            logging.debug(f'{row = }')
            logging.debug(f'{value = }')
            
            prop = addProperty(
                property,
                value,
                row=row,
                entry_callback = lambda val, prop = property: updateProperty(prop, val),
                label_callback = lambda name, prop = property: setProperty(name, value)
            )
            
            sizes.append(prop['size'])
            
            prop['label'].edit_start()
            
            self.properties['panned'].configure(height = sum(sizes))
        
        logging.debug(f'{row = }')
        
        add = ttk.Button(self.properties['frame'], text = 'Add', command = lambda *args, r = row + 1 : addNewProperty('Property', 0, r))
        add.pack(side = 'bottom', expand = True, fill = 'x')
        
        
    def resetProperties(self):
        
        for child in self.properties['frame'].winfo_children():
            if child != self.properties.get('panned', None):
                child.destroy()
        
        if not 'panned' in self.properties:
            self.properties['panned'] = ttk.PanedWindow(
                self.properties['frame'],
                orient='horizontal'
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
        
        def selectObject(event):
            item = self.object_selector['treeview'].focus()
            item = self.object_selector['treeview'].item(item)
            
            logging.info(item)
            
            if 'object' in item['tags']:
                id = item['values'][2]
                obj = self.level.getObjectById(id)
                self.selectObject(obj)
        
        self.object_selector['treeview'].bind('<ButtonRelease-1>', selectObject)
        self.object_selector['treeview'].bind('<Return>', selectObject)
    
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
        self.level_canvas.itemconfig(
            self.level_images['background'],
            image = self.level.PhotoImage
        )
        
        logging.info('updating level')
        
        self.selectedObject = None
        self.updateProperties()
        self.updateSelectionRectangle()
        self.updateObjectSelector()
        
        for obj in self.level.objects:
            self.updateObject(obj)
            logging.info('')
        
        self.updateLevelScroll()
        self.level_canvas.xview_moveto(0.23)
        self.level_canvas.yview_moveto(0.2)
    
    def dragObject(self, obj : wmwpy.classes.Object, event = None):
        logging.info(f'mouse pos = {(event.x, event.y)}')
        obj.pos = self.windowPosToWMWPos((event.x, event.y))
        
        self.updateObject(obj)
    
    def windowPosToWMWPos(self, pos : tuple = (0,0)):
        pos = numpy.array((self.level_canvas.canvasx(pos[0]),
                           self.level_canvas.canvasy(pos[1])))
        pos = pos / self.level.scale
        pos = pos / self.OBJECT_MULTIPLIER
        
        return tuple(pos)
    
    def getRelativeMousePos(self, pos : tuple, widget : tk.Widget):
        return numpy.array((numpy.array(pos) - (self.winfo_rootx(),
                             self.winfo_rooty())) - (widget.winfo_x(),
                                                     widget.winfo_y()))
    
    def selectObject(self, obj : wmwpy.classes.Object = None):
        self.selectedObject = obj
        # logging.debug(obj.name)
        logging.debug('object')
        
        self.updateObject(obj)
        self.updateProperties()
        self.updateSelectionRectangle()
        
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
                
                if item['values'][0] == obj.id:
                    selected = child
                    break
            
            if selected != None:
                self.object_selector['treeview'].selection_set(selected)
    
    def createMenubar(self):
        self.menubar = tk.Menu(self)
        self.config(menu = self.menubar)
        
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        
        self.file_menu.add_command(label = 'Open', command = self.openLevel)
        self.file_menu.add_command(label = 'Save', command = self.saveLevel)
        self.file_menu.add_command(label = 'Save as...', command = self.saveLevelAs)
        self.file_menu.add_separator()
        self.file_menu.add_command(label = 'Settings', command = self.showSettings)

        self.menubar.add_cascade(label = 'File', menu = self.file_menu)
        
        
        
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        
        self.help_menu.add_command(label = 'Discord', command = lambda *args : webbrowser.open(__links__['discord']))
        self.help_menu.add_command(label = 'About', command = self.showAbout)

        self.menubar.add_cascade(label = 'Help', menu = self.help_menu)
    
    def showAbout(self):
        about = popups.About(
            self,
            title = "About",
            author = __author__,
            program = "Where's My Editor?",
            version = __version__,
            description = """Where's My Editor? is a program to create and modify levels in the Where's My Water? game series.""",
            credits = __credits__,
            logo = Image.open(self.getAsset(self.LOGO)),
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
            initialdir = wmwpy.Utils.path.joinPath(
                self.game.gamepath,
                self.game.assets,
                self.game.baseassets,
                'Levels'
            )
        )
        
        if xml in ['', None]:
            logging.info('Open level canceled')
            return
        
        image = os.path.splitext(xml)[0] + '.png'
        
        self.loadLevel(xml, image)
    
    def saveLevel(self, *args, filename = None):
        xml = self.level.export()
        
        if filename == None:
            filename = wmwpy.Utils.path.joinPath(
                self.game.gamepath,
                self.game.assets,
                self.game.baseassets,
                self.level.filename,
            )
        
        try:
            with open(filename, 'wb') as file:
                file.write(xml)
            
            self.level._image.save(os.path.splitext(filename)[0] + '.png')
            
            messagebox.showinfo('Success', f'Successfully saved level to {filename}')
        except:
            messagebox.showerror('Error saving level', f'Unable to save level to {filename}')
        
    
    def saveLevelAs(self, *args):
        filename = filedialog.asksaveasfilename(
            initialfile = os.path.basename(self.level.filename),
            defaultextension = '.xml',
            filetypes = (
                ('WMW Level', '.xml'),
                ('Any', '*.*')
            ),
            initialdir = wmwpy.Utils.path.joinPath(
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
            return file
        
        path = pathlib.PurePath(path)
        assets = wmwpy.Utils.path.joinPath(
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
        if gamepath == '':
            gamepath = filedialog.askdirectory(
                parent = self,
                title = 'Select Game directory',
                mustexist = True,
            )
            self.settings.set('game.gamepath', gamepath)
        
        try:
            self.game = wmwpy.load(
                self.settings.get('game.gamepath'),
                assets = self.settings.get('game.assets'),
                game = self.settings.get('game.game'),
            )
        except:
            logging.warning(f'unable to load game: {self.settings.get("game.gamepath")}')
            wmwpy.Utils.logging_utils.log_exception()
    
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
            self.level_canvas.delete('selection')
        
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
            logging.warning('Unable to load level')
            log_exception()
            self.state = 'enabled'
            return
        
        logging.info(f'level = {self.level}')
        logging.info(f'objects = {self.level.objects}')
        
        self.level.scale = 5
        self.updateLevel()
        logging.info('finished loading level')
        self.state = 'enabled'
        return self.level
    
    def updateSettings(this):
        try:
            gamedir = this.settings.get('gamedir')
            this.settings.set('game.gamepath', gamedir)
            this.settings.remove('gamedir')
        except:
            pass
        try:
            default_level = this.settings.get('default_level')
            this.settings.set('game.default_level', default_level)
            this.settings.remove('default_level')
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
            fileio = io.StringIO()
            traceback.print_exc(file = fileio)
            
            logging.error(fileio.getvalue())

tk.CallWrapper = TkErrorCatcher

def main():
    try:
        app = WME(None)
        app.mainloop()
    except Exception as e:
        log_exception()

if(__name__ == '__main__'):
    main()
