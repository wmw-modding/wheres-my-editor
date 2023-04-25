import tkinter.filedialog as filedialog
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import popups
from PIL import Image, ImageTk
import json
import datetime
import os
from settings import Settings
from lxml import etree
import numpy

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

        self.currentObj = None
        self.level : wmwpy.classes.Level = None
        self.game : wmwpy.Game = None
        
        self.createMenubar()
        self.createWindow()
        
        self.loadGame()
        
        self.loadLevel(
            self.settings.get('game.default_level.xml'),
            self.settings.get('game.default_level.image')
        )
        self.updateLevel()

    def createWindow(self):
        self.seperator = ttk.PanedWindow(orient='horizontal')
        self.seperator.pack(fill=tk.BOTH, expand=1)

        self.side_pane = ttk.PanedWindow(self.seperator, orient='vertical')
        self.seperator.add(self.side_pane)

        self.objects_frame = ttk.Frame(self.side_pane, width=200, height=300)
        self.side_pane.add(self.objects_frame)

        self.properties_frame = ttk.Frame(self.side_pane, width=200, height=300)
        self.side_pane.add(self.properties_frame)

        self.level_canvas = tk.Canvas(self.seperator, width=90*self.scale, height=120*self.scale)
        self.seperator.add(self.level_canvas)
        
        self.level_images = {
            'background': self.level_canvas.create_image(
            0,0, anchor = 'c', image = None
        ),
            'objects': {}
        }
    
    def updateObject(self, obj : wmwpy.classes.Object):
        photoImage = obj.PhotoImage
        pos = numpy.array(obj.pos)
        
        pos = (pos * [1.25,-1.3]) * self.level.scale
        
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
            self.level_images['objects'][obj.name] = self.level_canvas.create_image(
                pos[0],
                pos[1],
                anchor = 'c',
                image = photoImage,
            )
    
    def updateLevel(self):
        self.level_canvas.itemconfig(
            self.level_images['background'],
            image = self.level.PhotoImage
        )
        
        self.level_canvas.config(scrollregion=((self.level.image.size[0] / 2) * -1,(self.level.image.size[1] / 2) * -1, (self.level.image.size[0] / 2), (self.level.image.size[1] / 2)))
        
        for obj in self.level.objects:
            self.updateObject(obj)
        
    
    def createMenubar(self):
        self.menubar = tk.Menu(self)
        self.config(menu = self.menubar)
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        
        self.file_menu.add_command(label = 'Open', command = self.openLevel)
        self.file_menu.add_command(label = 'Save', command = self.saveLevel)
        self.file_menu.add_command(label = 'Save as...', command = self.saveLevelAs)
        self.menubar.add_cascade(label = 'File', menu = self.file_menu)
    
    def openLevel(self, *args):
        pass
    
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
