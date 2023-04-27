import tkinter.filedialog as filedialog
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import tkwidgets
import popups
from PIL import Image, ImageTk
import json
import datetime
import os
from settings import Settings
from lxml import etree
import numpy
import typing

import wmwpy

class WME(tk.Tk):
    def __init__(self, parent):
        tk.Tk.__init__(self,parent)
        #tk.Tk.iconbitmap(self, default = 'assets/logo.xbm')
        self.parent = parent
        
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
        
        self.loadLevel(
            self.settings.get('game.default_level.xml'),
            self.settings.get('game.default_level.image')
        )

    def createWindow(self):
        self.seperator = ttk.PanedWindow(orient='horizontal')
        self.seperator.pack(fill=tk.BOTH, expand=1)

        self.side_pane = ttk.PanedWindow(self.seperator, orient='vertical')
        self.seperator.add(self.side_pane)

        self.objects_frame = ttk.Frame(self.side_pane, width=200, height=300)
        self.side_pane.add(self.objects_frame)
        
        self.properties = {
            'frame' : ttk.Frame(self.side_pane, width=200, height=300)
        }
        self.side_pane.add(self.properties['frame'])

        self.level_canvas = tk.Canvas(self.seperator, width=90*self.scale, height=120*self.scale)
        self.seperator.add(self.level_canvas)
        
        self.level_images = {
            'background': self.level_canvas.create_image(
            0,0, anchor = 'c', image = None
        ),
            'objects': {}
        }
        
        self.resetProperties()
    
    OBJECT_OFFSET = [1.25,-1.3]
    
    def updateObject(self, obj : wmwpy.classes.Object):
        photoImage = obj.PhotoImage
        pos = numpy.array(obj.pos)
        offset = numpy.array(obj.offset)
        
        pos = pos - (offset * [1,-1])
        pos = (pos * self.OBJECT_OFFSET) * self.level.scale
        
        if obj.name in self.level_images['objects']:
            id = self.level_images['objects'][obj.name]
            self.level_canvas.itemconfig(
                id,
                image = photoImage,
            )
            
            self.level_canvas.moveto(
                id,
                pos[0],
                pos[1],
            )
        else:
            id = self.level_images['objects'][obj.name] = self.level_canvas.create_image(
                pos[0],
                pos[1],
                anchor = 'c',
                image = photoImage,
            )
        
        self.level_canvas.tag_bind(
            id,
            '<Button1-Motion>',
            lambda e: self.dragObject(obj, e)
        )
        self.level_canvas.tag_bind(
            id,
            '<ButtonRelease-1>',
            lambda e: self.selectObject(obj)
        )
    
    def updateProperties(self, obj : wmwpy.classes.Object = None):
        if obj == None:
            obj = self.selectedObject
        
        self.resetProperties()
        
        ROW_SIZE = 25
        
        def addProperty(
            property : str,
            value : str,
            type : typing.Literal['number', 'text'] = 'text',
            removable = True,
            row = 0,
            entry_callback : typing.Callable[[str], typing.Any] = None,
            label_callback : typing.Callable[[str], bool] = None,
            **kwargs,
        ):
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
            
            type = type.lower()
            
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
            
            input.grid(column = 0, row=row, sticky = 'we')
            if entry_callback:
                input.bind('<Return>', lambda e: entry_callback(input.get()))
                input.bind('<FocusOut>', lambda e: entry_callback(input.get()))
            
            if removable:
                removeButton = ttk.Button(
                    self.properties['right'],
                    text='-',
                    width=2,
                )
                removeButton.grid(column=1, row=row)
            
            self.properties['left'].rowconfigure(row, minsize=ROW_SIZE)
            self.properties['right'].rowconfigure(row, minsize=ROW_SIZE)
    
        def updateProperty(property, value):
            obj.properties[property] = value
            self.updateObject(obj)
        
        def updatePropertyName(property, newName):
            if newName == property:
                return True
            print(f'{newName = }')
            print(f'{property = }')
            
            if newName in obj.properties:
                messagebox.showerror(
                    'Property name already exists',
                    f'Property "{newName}" already exists.'
                )
                
                return False
            else:
                value = obj.properties[property]
                del obj.properties[property]
                obj.properties[newName] = value
                
                self.updateObject(obj)
                self.updateProperties(obj)
                
                return True
        
        addProperty('Name', obj.name, 'text', removable = False, row=0)
        angle = '0'
        if 'Angle' in obj.properties:
            angle = obj.properties['Angle']
        addProperty(
            'Angle',
            angle,
            'number',
            removable = False,
            row=1,
            from_=-360,
            to=360,
            entry_callback = lambda value: updateProperty('Angle', value),
        )
        
        row = 1
        
        for property in obj.properties:
            if property not in ['Angle']:
                row += 1
                addProperty(
                    property,
                    obj.properties[property],
                    row=row,
                    entry_callback = lambda value, prop = property: updateProperty(prop, value),
                    label_callback = lambda name, prop = property: updatePropertyName(prop, name)
                )
        
    def resetProperties(self):
        
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
            self.properties['right'].columnconfigure(0, weight = 4)
            # self.properties['right'].columnconfigure(1, weight = 1)
    
    def updateLevel(self):
        self.level_canvas.itemconfig(
            self.level_images['background'],
            image = self.level.PhotoImage
        )
        
        self.level_canvas.config(scrollregion=((self.level.image.size[0] / 2) * -1,(self.level.image.size[1] / 2) * -1, (self.level.image.size[0] / 2), (self.level.image.size[1] / 2)))
        
        for obj in self.level.objects:
            self.updateObject(obj)
    
    def dragObject(self, obj : wmwpy.classes.Object, event = None):
        pos = numpy.array((self.level_canvas.canvasx(event.x), self.level_canvas.canvasy(event.y)))
        pos = pos / self.level.scale
        pos = pos / self.OBJECT_OFFSET
        
        obj.pos = tuple(pos)
        
        self.updateObject(obj)
    
    def selectObject(self, obj : wmwpy.classes.Object = None):
        self.selectedObject = obj
        print(obj.name)
        
        self.updateProperties()
        
    
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
        pass
    
    def saveLevelAs(self, *args):
        pass
    
    def getFile(self, path : str):
        if path.startswith(':game:'):
            path = path.partition(':game:')[-1]
            
            file = self.game.filesystem.get(path)
        
        elif path in ['', None]:
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
            pass
    
    def loadLevel(self, xml : str, image : str):
        if self.game in ['', None]:
            return
        xml = self.getFile(xml)
        image = self.getFile(image)
        
        try:
            self.level = self.game.Level(xml, image)
        except:
            print('Unable to load level')
        
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

def main():
    # app.display()
    app = WME(None)
    app.mainloop()

if(__name__ == '__main__'):
    main()
