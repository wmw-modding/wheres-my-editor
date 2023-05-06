__version__ = '2.0.0'
__author__ = 'ego-lay-atman-bay'
__credits__ = [
    {
        'name' : 'wmwpy',
        'url' : 'https://github.com/wmw-modding/wmwpy',
        'description' : "Where's My Editor? uses wmwpy to read and modify Where's My Water? data, e.g. levels."
    },
    {
        'name' : 'Rubice',
        'url' : '',
        'description' : 'Thanks to @rubice for creating the logo.'
    },
    {
        'name' : 'campbellsonic',
        'url' : 'https://github.com/campbellsonic',
        'description' : 'Thanks to @campbellsonic for helping to read waltex images.'
    }
]

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

import tkinter.filedialog as filedialog
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import tkwidgets
from PIL import Image, ImageTk, ImageColor, ImageDraw
import json
from settings import Settings
from lxml import etree
import numpy
import typing
from copy import copy
import pathlib

import wmwpy
from scrollframe import ScrollFrame
import popups

if wmwpy.__version__ < "0.2.0-beta":
    logging.error('wmwpy version must be "0.2.0-beta" or higher.')
    exit()

ImageColor.colormap['transparent'] = '#0000'

class WME(tk.Tk):
    APP_ICONS = [
            'assets/images/icon.png',
        ]
    
    def __init__(self, parent):
        tk.Tk.__init__(self,parent)
        self.parent = parent
        
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            self.WME_assets = sys._MEIPASS
        else:
            self.WME_assets = '.'
        
        self.findIcons()
        if len(self.windowIcons) > 0:
            self.iconphoto(True, *self.windowIcons)
        
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
    
    def findIcons(self):
        self.windowIcons = []
        
        for icon in self.APP_ICONS:
            try:
                self.windowIcons.append(
                    ImageTk.PhotoImage(
                        Image.open(os.path.join(self.WME_assets, icon))
                    )
                )
            except:
                pass
        
        return self.windowIcons

    def createWindow(self):
        self.seperator = ttk.PanedWindow(orient='horizontal')
        self.seperator.pack(fill=tk.BOTH, expand=1)

        self.side_pane = ttk.PanedWindow(self.seperator, orient='vertical')
        self.seperator.add(self.side_pane)
        
        side_pane_width = 200
        side_pane_height = 300
        
        self.object_selector : dict[str, tk.Widget | ttk.Treeview] = {
            'labelFrame' : ttk.LabelFrame(self.side_pane, width=side_pane_width, height=side_pane_height, text='Objects'),
            'treeview' : None,
            'y_scroll' : None,
            'x_scroll' : None,
        }
        self.side_pane.add(self.object_selector['labelFrame'])
        
        self.object_selector['treeview'] = ttk.Treeview(
            self.object_selector['labelFrame'],
            show = 'tree',
            name = 'objects'
        )
        
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
            'scrollFrame',
            'frame',
            'panned',
            'left',
            'right',
        ], tk.Widget] = {
            'labelFrame' : ttk.LabelFrame(self.side_pane, width=side_pane_width, height=side_pane_height, text='Properties')
        }
        self.side_pane.add(self.properties['labelFrame'])
        
        self.properties['scrollFrame'] = ScrollFrame(self.properties['labelFrame'], usettk=True, width=200,)
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
        
        if platform.system() == 'Linux':
            self.level_canvas.bind("<Button-4>", self.onLevelMouseWheel)
            self.level_canvas.bind("<Button-5>", self.onLevelMouseWheel)
            
            self.level_canvas.bind("<Shift-Button-4>", lambda *args: self.onLevelMouseWheel(*args, type = 1))
            self.level_canvas.bind("<Shift-Button-5>", lambda *args: self.onLevelMouseWheel(*args, type = 1))
        else:
            self.level_canvas.bind("<MouseWheel>", self.onLevelMouseWheel)
            self.level_canvas.bind("<Shift-MouseWheel>", lambda *args: self.onLevelMouseWheel(*args, type = 1))
        
        self.level_canvas.bind('<Button-1>', self.onLevelClick)
        self.createLevelContextMenu()
        self.level_canvas.bind('<Button-3>', self.onLevelRightClick)
        
        self.resetProperties()
    
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
            logging.info('deleted selection')
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
        
        pos = pos - (offset * [1,-1])
        pos = (pos * self.OBJECT_MULTIPLIER) * self.level.scale
        
        return pos
    
    def updateObject(self, obj : wmwpy.classes.Object):
        if obj == None:
            self.updateSelectionRectangle()
            self.updateLevelScroll()
            return
        
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
        logging.info(f"pos: {pos}\n")
        
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
            return
        
        ROW_SIZE = 25
        
        def addProperty(
            property : str,
            value : str,
            type : typing.Literal['number', 'text'] = 'text',
            removable = True,
            row = 0,
            entry_callback : typing.Callable[[str], typing.Any] = None,
            label_callback : typing.Callable[[str], bool] = None,
            remove_callback : typing.Callable = None,
            **kwargs,
        ) -> dict[typing.Literal['label', 'inputs', 'remove'], tkwidgets.EditableLabel | list[ttk.Entry] | ttk.Button]:
            if removable:
                name = tkwidgets.EditableLabel(
                    self.properties['left'],
                    text = property,
                    callback = label_callback,
                )
            else:
                name = ttk.Label(
                    self.properties['left'],
                    text=property,
                )
            name.grid(row=row, sticky='we')
            
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
                    input.grid(column = column, row=row, sticky='we')
                    if entry_callback:
                        input.bind('<Return>', lambda e, value = input.get, col = column: entry_callback(value(), col))
                        input.bind('<FocusOut>', lambda e, value = input.get, col = column: entry_callback(value(), col))
                    
                    column += 1
                    
                    inputs.append(input)
                    
            else:
                type = type.lower()
                
                input = inputType(type, value)
                input.grid(column = 0, row=row, sticky = 'we', columnspan=2)
                
                if entry_callback:
                    input.bind('<Return>', lambda e: entry_callback(input.get()))
                    input.bind('<FocusOut>', lambda e: entry_callback(input.get()))
                
                inputs.append(input)
            
            removeButton = None
            
            if removable:
                removeButton = ttk.Button(
                    self.properties['right'],
                    text='-',
                    width=2,
                    command = remove_callback
                )
                removeButton.grid(column=2, row=row)
            
            self.properties['left'].rowconfigure(row, minsize=ROW_SIZE)
            self.properties['right'].rowconfigure(row, minsize=ROW_SIZE)
            
            return {
                'label' : name,
                'inputs' : inputs,
                'remove' : removeButton,
            }
        
        def removePropety(property):
            if property in obj.properties:
                del obj.properties[property]
                self.updateObject(obj)
                self.updateProperties(obj)
    
        def updateProperty(property, value):
            obj.properties[property] = value
            self.updateObject(obj)
        
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
        
        addProperty('Name', obj.name, 'text', removable = False, row=0)
        addProperty('Pos', obj.pos, ['number', 'number'], removable=False, row=1, entry_callback = lambda value, col : updatePosition(value, col), from_ = -99, to = 99)
        
        angle = '0'
        if 'Angle' in obj.properties:
            angle = obj.properties['Angle']
        addProperty(
            'Angle',
            angle,
            'number',
            removable = False,
            row=2,
            from_=-360,
            to=360,
            entry_callback = lambda value: updateProperty('Angle', value),
        )
        
        row = 3
        
        for property in obj.properties:
            if property not in ['Angle']:
                row += 1
                logging.debug(f'{property = }')
                addProperty(
                    property,
                    obj.properties[property],
                    row=row,
                    entry_callback = lambda value, prop = property: updateProperty(prop, value),
                    label_callback = lambda name, prop = property: updatePropertyName(prop, name),
                    remove_callback = lambda *args, prop = property : removePropety(prop),
                )
        
        self.properties['panned'].configure(height = row * ROW_SIZE)
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
            
            prop['label'].edit_start()
            
            self.properties['panned'].configure(height = row * ROW_SIZE)
        
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
        
        root = self.object_selector['treeview'].insert(
            '',
            'end',
            iid = 'root',
            text = 'Objects',
            open = True,
            tags = 'root',
            
        )
        
        for obj in self.level.objects:
            self.object_selector['treeview'].insert(
                root,
                'end',
                text = obj.name,
                open = True,
                values = [obj.id],
                tags = 'object'
            )
        
        def selectObject(event):
            item = self.object_selector['treeview'].focus()
            item = self.object_selector['treeview'].item(item)
            
            logging.info(item)
            
            if 'object' in item['tags']:
                id = item['values'][0]
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
        coords = coords.swapaxes(0,1)
        
        min = numpy.array([a.min() for a in coords]) - LEVEL_CANVAS_PADDING
        max = numpy.array([a.max() for a in coords]) + LEVEL_CANVAS_PADDING
        
        
        min = numpy.append(min, level_size[0]).reshape([2,2]).swapaxes(0,1)
        max = numpy.append(max, level_size[1]).reshape([2,2]).swapaxes(0,1)
        
        logging.debug(f'{max = }')
        logging.debug(f'{min = }')
        
        min = [a.min() for a in min]
        max = [a.max() for a in max]
        
        scrollregion = tuple(numpy.append(min,max))
        
        logging.debug(f'scrollregion = {scrollregion}')
        
        self.level_canvas.config(scrollregion = scrollregion)
        
    
    def updateLevel(self):
        self.level_canvas.itemconfig(
            self.level_images['background'],
            image = self.level.PhotoImage
        )
        
        self.selectedObject = None
        self.updateProperties()
        self.updateSelectionRectangle()
        self.updateObjectSelector()
        
        for obj in self.level.objects:
            self.updateObject(obj)
        
        self.level_canvas.xview_moveto(0.15)
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
            children = self.object_selector['treeview'].get_children('root')
            
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
        self.menubar.add_cascade(label = 'File', menu = self.file_menu)
    
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
        
        image = os.path.splitext(xml)[0] + '.png'
        
        self.loadLevel(xml, image)
    
    def saveLevel(self, *args, filename = None):
        xml = self.level.export()
        
        if filename == None:
            filename = wmwpy.Utils.path.joinPath(
                self.game.gamepath,
                self.game.assets,
                self.game.baseassets,
                '/Levels/',
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
        if not isinstance(path, str):
            raise TypeError('path must be str')
        
        if path.startswith(':game:'):
            path = path.partition(':game:')[-1]
            
            file = self.game.filesystem.get(path)
            return file
        
        path = pathlib.PurePath(path)
        assets = wmwpy.Utils.path.joinPath(
            self.game.gamepath,
            self.game.assets,
        )
        
        print(f'In filesystem? {path.is_relative_to(assets)}')
        if path.is_relative_to(assets):
            file = self.game.filesystem.get(os.path.relpath(path, assets))
            return file
        
        if path in ['', None]:
            return None
        else:
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
    
    def loadLevel(self, xml : str, image : str):
        if self.game in ['', None]:
            return
        xml = self.getFile(xml)
        image = self.getFile(image)
        
        if isinstance(self.level, wmwpy.classes.Level):
            self.level_canvas.delete('object')
        
        # try:
        self.level = self.game.Level(xml, image)
        # except:
        #     logging.warning('Unable to load level')
        #     return
        
        self.level.scale = 5
        self.updateLevel()
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
        fileio = io.StringIO()
        traceback.print_exc(file = fileio)
        
        logging.error(fileio.getvalue())

if(__name__ == '__main__'):
    main()
