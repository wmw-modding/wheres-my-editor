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
    
    def createMenubar(self):
        self.menubar = tk.Menu(self)
        self.config(menu = self.menubar)
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        
        self.file_menu.add_command(label = 'Open')
    
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
        
        self.game = wmwpy.load(
            self.settings.get('game.gamepath'),
            assets = self.settings.get('game.assets'),
            game = self.settings.get('game.game'),
        )
    
    def loadLevel(self, xml : str, image : str):
        xml = self.getFile(xml)
        image = self.getFile(image)
        
        # try:
        self.level = self.game.Level(xml, image)
        # except:
        #     raise FileNotFoundError('Unable to load level')
        
        return self.level

def main():
    # app.display()
    app = WME(None)
    app.mainloop()

if(__name__ == '__main__'):
    main()
