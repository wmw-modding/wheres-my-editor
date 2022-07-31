from tkinter.filedialog import FileDialog
import tkinter as tk
from tkinter import ttk, simpledialog
from guizero import *
import popups
from PIL import Image, ImageTk
from xmlviewer import XML_Viwer, autoscroll
from getObject import *
import itertools
import json

import lxml
from lxml import etree

images = []

class Window(tk.Tk):
    def __init__(self, parent):
        tk.Tk.__init__(self,parent)
        #tk.Tk.iconbitmap(self, default = 'assets/logo.xbm')
        self.parent = parent
        self.level_canvas = tk.Canvas(parent, width=90*5, height=120*5)
        self.objects_canvas = tk.Canvas(parent, width=200, height=300)
        self.prop_canvas = tk.Canvas(parent, width=200, height=300)

        self.scale = 5
        
        self.loadSettings()


        # image = Image.open(self.gamedir + 'assets/Levels/_seb_test_3_mystery.png')
        # image = image.resize((image.width*self.scale, image.height*self.scale), Image.Resampling.NEAREST)
        # self.level_img = ImageTk.PhotoImage(image=image)

        self.objects = []
            
        self.initialize()

        self.title("Where's my Editor")
        self.geometry('%dx%d' % (760 , 610) )

    def initialize(self):
        self.grid()
    
        self.level_canvas.grid(row=0, column=1, rowspan=2)
        self.objects_canvas.grid(row=0, column=0)
        self.prop_canvas.grid(row=1, column=0)
        self.level_xml = '<root></root>'
        self.level_size = (90 * self.scale, 120 * self.scale)

        if self.settings['default_level']['image'] != '':
            self.open_level_img(self.settings['default_level']['image'])

        if self.settings['default_level']['xml'] != '':
            self.open_level_xml(self.settings['default_level']['xml'])
            # with open(self.settings['default_level']['xml']) as file:
                # self.level_xml = file.read()
        
        self.xml_viewer = XML_Viwer(self.objects_canvas, self.level_xml, heading_text='objects').pack()
        print(self.xml_viewer)
        time.sleep(2)

        # self.level_img_index = self.level_canvas.create_image(0,0, image=None, anchor='nw')

        buttons = ttk.LabelFrame(self.prop_canvas, text='properties')
        ttk.Button(buttons, text='Add', command=self.action).pack()

        self.prop_buttons = self.prop_canvas.create_window(0, 0, anchor='nw', window=buttons)

        # self.openIMG('blank.png')
        
        # self.canvas.tag_bind('object', '<ButtonPress-1>', self.on_press)
        # self.canvas.tag_bind('bg', '<ButtonPress-1>', self.destroyTweaks)
        # self.canvas.tag_bind('object', '<ButtonRelease-1>', self.on_obj_release)
        # self.canvas.tag_bind('object', '<B1-Motion>', self.on_obj_motion)
        #self.bind('<Motion>', self.xy)
        
        # this data is used to keep track of an item being dragged
        # self._drag_data = {'x': 0, 'y': 0, 'item': None}

        
        # button
        # buttonBox = ttk.LabelFrame(self, text='Toolbox')
        # buttonBox.grid(row=1, column=0, rowspan = 99, sticky = 'N')
        # ttk.Button(buttonBox, text='Add', command = self.action).pack()
        # ttk.Button(buttonBox, text='Copy', command = self.action).pack()
        # ttk.Button(buttonBox, text='Paste', command = self.action).pack()
        # ttk.Button(buttonBox, text='MultiSeclect', command = popups.commingsoon).pack()
        # ttk.Button(buttonBox, text='Seclect All', command = popups.commingsoon).pack()
        # ttk.Button(buttonBox, text='Undo', command = popups.commingsoon).pack()
        # ttk.Button(buttonBox, text='Redo', command = popups.commingsoon).pack()
        
        # obj prop tweak
        # ttk.Label(self, text='OBJECT PROPERTIES').grid(row=0, column=3)
        #ttk.Button(self, text='Apply', command = popups.applyCommingsoon).grid(row=99, column=3)
        
        # menu bar
        bar = tk.Menu(self)
        
        self.config(menu=bar)
        
        fileMenu = tk.Menu(bar, tearoff=0)
        
        fileMenu.add_command(label= 'Open png', command = self.open_png)
        fileMenu.add_command(label='Open XML', command=self.open_xml)
        # fileMenu.add_command(label= 'Export XML', command = export)
        # fileMenu.add_command(label= 'Close Img', command = lambda: self.openIMG('assets/WMWmap.png'))
        fileMenu.add_separator()
        # fileMenu.add_command(label= 'Exit', command = self.client_exit)
        bar.add_cascade(label= 'File', menu=fileMenu)
        
        edit = tk.Menu(bar, tearoff=0)
        # edit.add_command(label= 'Copy', command = popups.commingsoon)
        # edit.add_command(label= 'Paste', command = popups.commingsoon)
        #bar.add_cascade(label= 'Edit', menu=edit)
        
        help = tk.Menu(bar, tearoff=0)
        help.add_command(label= 'View help.txt')
        help.add_command(label= 'About', command = popups.about_dialog)
        bar.add_cascade(label= 'Help', menu=help)

        # object_viewer = tk.Canvas(highlightthickness=border, highlightbackground='black')
        # window = self.level_canvas.create_window(0, 0, anchor='nw', window=display)

        # bomb = object('game/wmw/assets/Objects/bomb.hs')
        # display = self.level_canvas.create_image(50, 100, anchor='nw', image=ImageTk.PhotoImage(bomb.image))
        # print('display: ' + str(display))
        # bomb.playAnimation(self, self.level_canvas, display, bomb.sprites[0].animations[0])
        self.mouseUp()

        self.addObj(self.gamedir + '/assets/Objects/bomb.hs', pos=(0,20))
        self.addObj(self.gamedir + '/assets/Objects/bomb.hs', pos=(0,0))

        self.level_canvas.bind('<B1-Motion>', self.moveObj)
        self.level_canvas.bind('<ButtonRelease-1>', self.mouseUp)

    def action(self):
        pass

    def open_png(self):
        path = filedialog.askopenfilename(title='Open level image', defaultextension="*.png", filetypes=(('wmw level', '*.png'),('any', '*.*')), initialdir=self.gamedir+'assets/Levels')
        self.open_level_img(path)

    def open_xml(self):
        path = filedialog.askopenfilename(title='Open level XML', defaultextension="*.xml", filetypes=(('wmw level', '*.xml'),('any', '*.*')), initialdir=self.gamedir+'assets/Levels')
        self.open_level_xml(path)

    def open_level_img(self, path):
        try:
            self.level_img_index
        except:
            self.level_img_index = self.level_canvas.create_image(0,0, image=None, anchor='nw')

        image = Image.open(path)
        image = image.resize((image.width*self.scale, image.height*self.scale), Image.Resampling.NEAREST)
        self.level_img = ImageTk.PhotoImage(image=image)
        self.level_size = (image.width, image.height)

        self.level_canvas.itemconfig(self.level_img_index, image=self.level_img)

    def open_level_xml(self, path):
        with open(path) as file:
            self.level_xml = file.read()
            xml = etree.fromstring(self.level_xml)
            print(xml)

        global images
        self.objects = []
        images = []

        root = xml
        
        for obj in range(len(root)):
            if root[obj].tag == 'Object':
                object = {}
                object['name'] = root[obj].get('name')
                pos = root[obj][findTag(root[obj], 'AbsoluteLocation')].get('value').split()
                object['pos'] = (float(pos[0]), float(pos[1]))

                object['properties'] = {}
                for prop in root[obj][findTag(root[obj], 'Properties')]:
                    object['properties'][prop.get('name')] = prop.get('value')

                print(object)

                self.addObj(self.gamedir + 'assets/' + object['properties']['Filename'], pos = object['pos'], properties=object['properties'])




    def truePos(self, pos):
        x = pos[0] * 1 * self.scale
        y = pos[1] * -1 * self.scale

        x = x + (self.level_size[0] / 2)
        y = y + (self.level_size[1] / 2)

        return (x,y)

    def gamePos(self, pos):
        x = pos[0]
        y = pos[1]

        x = x - (self.level_size[0] / 2)
        y = y - (self.level_size[1] / 2)

        x = x / self.scale
        y = y / self.scale

        return (x,y)

    def addObj(self, path, pos=(0,0), properties={}):

        obj = newObject(path,pos=pos, properties=properties)
        newPos = self.truePos(pos)
        print(newPos)

        object = {}
        object['object'] = obj
        global images
        # obj.image = obj.image.resize((obj.image.width + 5, obj.image.height + 5))
        print(properties)

        try:
            angle = float(obj.properties['Angle'])
        except:
            angle = 0

        img = ImageTk.PhotoImage(obj.image.rotate(angle, expand=True))
        images.append(img)
        object['size'] = obj.image.size
        print(object['size'])

        object['image'] = self.level_canvas.create_image(newPos[0], newPos[1], anchor='center', image=img)
        print(self.level_canvas.coords(object['image']))

        self.objects.append(object)

    def moveObj(self, event):
        if self.currentObj == None and not self.mouseDown:
            self.currentObj = next((self.objects.index(obj) for obj in self.objects[::-1] if (event.x >= self.level_canvas.coords(obj['image'])[0] - (obj['size'][0] / 2) and event.x <= int(self.level_canvas.coords(obj['image'])[0]) + int(obj['size'][0]) / 2) and (event.y >= self.level_canvas.coords(obj['image'])[1] - (obj['size'][1] / 2) and event.y <= int(self.level_canvas.coords(obj['image'])[1]) + int(obj['size'][1]) / 2)), None)
            print(self.currentObj)
            self.prevMousePos = (event.x, event.y)
        
        if self.currentObj != None:
            self.level_canvas.move(self.objects[self.currentObj]['image'], event.x - self.prevMousePos[0], event.y - self.prevMousePos[1])
            self.objects[self.currentObj]['object'].pos = self.gamePos(self.level_canvas.coords(self.objects[self.currentObj]['image']))
            print(self.objects[self.currentObj]['object'].pos)
            print(self.currentObj)

            self.prevMousePos = (event.x, event.y)
        
        self.mouseDown = True


    def mouseUp(self, e=None):
        self.currentObj = None
        self.prevMousePos = None
        self.mouseDown = False
        print(self.currentObj)

    def initSettings(self):
        self.gamedir =  filedialog.askdirectory(title='Select game Directory')
        
        self.settings = {
            "gameDir" : self.gamedir,
            "default_level" : {
                "image" : '',
                "xml" : ''
            }
        }

    def loadSettings(self):
        try:
            with open('settings.json', 'r') as file:
                self.settings = json.load(file)
        except:
            self.initSettings()
            self.exportSettings()
        
        self.gamedir = self.settings['gameDir']

    def exportSettings(self):
        file = open('settings.json', 'w+')
        json.dump(self.settings, file, indent=2)
        

def main():
    # app.display()
    app = Window(None)
    app.mainloop()

if(__name__ == '__main__'):
    main()
