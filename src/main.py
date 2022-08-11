from threading import Thread
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
        self.scale = 5

        self.seperator = ttk.PanedWindow(orient='horizontal')
        self.seperator.pack(fill=tk.BOTH, expand=1)

        self.side_pane = ttk.PanedWindow(self.seperator, orient='vertical')
        self.seperator.add(self.side_pane)

        self.objects_canvas = tk.Canvas(self.side_pane, width=200, height=300)
        self.side_pane.add(self.objects_canvas)

        self.prop_canvas = tk.Canvas(self.side_pane, width=200, height=300)
        self.side_pane.add(self.prop_canvas)

        self.level_canvas = tk.Canvas(self.seperator, width=90*self.scale, height=120*self.scale)
        self.seperator.add(self.level_canvas)

        self.style = ttk.Style()

        
        self.loadSettings()

        self.active = True

        # image = Image.open(self.gamedir + 'assets/Levels/_seb_test_3_mystery.png')
        # image = image.resize((image.width*self.scale, image.height*self.scale), Image.Resampling.NEAREST)
        # self.level_img = ImageTk.PhotoImage(image=image)

        self.objects = []
        self.currentObj = None
            
        self.initialize()

        self.title("Where's my Editor")
        self.geometry('%dx%d' % (760 , 610) )

    def initialize(self):
        self.grid()
    
        # self.level_canvas.grid(row=0, column=2, rowspan=2)
        # self.side_pane.grid(row=0, column=0, rowspan=2)
        # self.objects_canvas.grid(row=0, column=0)
        # self.prop_canvas.grid(row=1, column=0)
        self.level_xml = '<root></root>'
        self.level_size = (90 * self.scale, 120 * self.scale)


        if self.settings['default_level']['image'] != '':
            self.open_level_img(self.settings['default_level']['image'])
        else:
            self.open_level_img()

        if self.settings['default_level']['xml'] != '':
            self.open_level_xml(self.settings['default_level']['xml'])
            # with open(self.settings['default_level']['xml']) as file:
                # self.level_xml = file.read()
        
        self.xml_viewer = XML_Viwer(self.objects_canvas, self.level_xml, heading_text='objects').pack()
        print(self.xml_viewer)
        # time.sleep(2)

        # self.level_img_index = self.level_canvas.create_image(0,0, image=None, anchor='nw')

        self.prop_frame = ttk.LabelFrame(self.prop_canvas, text='properties')

        self.prop_panedWindow = ttk.PanedWindow(self.prop_frame, orient='horizontal')

        self.prop_left_frame = ttk.Frame(self.prop_panedWindow, width=50)
        self.prop_panedWindow.add(self.prop_left_frame)

        self.prop_right_frame = ttk.Frame(self.prop_panedWindow, width=50)
        self.prop_panedWindow.add(self.prop_right_frame)

        # self.prop_frame.columnconfigure(1, weight=1)
        # self.prop_frame.rowconfigure(0, weight=1)

        self.prop_panedWindow.grid(column=0, row=0)
        
        ttk.Button(self.prop_left_frame, text='Add', command=self.action).pack()
        self.prop_right_frame.columnconfigure(0, weight=3)
        self.prop_right_frame.bind('<Configure>', self.prop_right_resize)

        self.prop_buttons = self.prop_canvas.create_window(0, 0, anchor='nw', window=self.prop_frame, width=200)
        self.prop_canvas.bind('<Configure>', self.prop_resize)

        self.prop_scrollbar = ttk.Scrollbar(self.prop_canvas, orient='vertical', command=self.prop_canvas.yview)
        self.prop_scrollbar.pack(side='right', fill='both')

        self.prop_canvas.config(yscrollcommand=self.prop_scrollbar.set)

        
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

        # self.addObj(self.gamedir + '/assets/Objects/bomb.hs', pos=(0,20))
        # self.addObj(self.gamedir + '/assets/Objects/bomb.hs', pos=(0,0))

        self.level_canvas.bind('<B1-Motion>', self.moveObj)
        self.level_canvas.bind('<ButtonRelease-1>', self.mouseUp)

        self.bind_all("<Button-1>", lambda event: event.widget.focus_set())
        self.bind('<KeyPress-Return>', lambda e: self.focus_set())

    def action(self):
        pass

    def prop_right_resize(self, e):
        for c in self.prop_right_frame.winfo_children():
            c.configure(width=e.width - 20)

    def prop_resize(self, e):
        print(e.width,e.height)
        sb_width = self.prop_scrollbar.winfo_width()
        print(sb_width)
        self.prop_canvas.itemconfig(self.prop_buttons, width=e.width - sb_width)
        self.prop_panedWindow.config(width=e.width - sb_width - 2)

    def updateProps(self):
        def callback(var, index, mode):
            print(self.current_props['Angle'].get())

        def update_sprite():
            print(self.current_props['Angle'].get())
            return True

        for c in self.prop_left_frame.winfo_children():
            c.destroy()

        for c in self.prop_right_frame.winfo_children():
            c.destroy()
        
        row = 0
        if self.currentObj:
            self.current_props = {
                'Angle' : tk.StringVar()
            }

            print(self.objects[self.currentObj]['object'].properties)
            properties = self.objects[self.currentObj]['object'].properties

            label = ttk.Label(self.prop_left_frame, text='Angle')
            label.grid(column=0, row=row, sticky='w')
            self.prop_left_frame.rowconfigure(row, minsize=21)

            # self.current_props['Angle'].trace_add('write', callback=callback)

            value = ttk.Spinbox(self.prop_right_frame, textvariable=self.current_props['Angle'], from_=-360, to=360, validate='focusout', validatecommand=self.update_current_obj)
            value.delete(0, 'end')
            value.insert(0, self.objects[self.currentObj]['object'].properties['Angle'])
            value.grid(column=0, row=row, sticky='w')
            self.prop_right_frame.rowconfigure(row, minsize=21)

            row += 1

            for key in properties:
                if not key.lower() in ['angle']:
                    label = ttk.Label(self.prop_left_frame, text=key)
                    label.grid(column=0, row=row, sticky='w')
                    self.prop_left_frame.rowconfigure(row, minsize=21)

                    self.current_props[key] = tk.StringVar()

                    value = ttk.Entry(self.prop_right_frame, textvariable=self.current_props[key], validate='focusout', validatecommand=self.update_current_obj)
                    value.delete(0, 'end')
                    value.insert(0, self.objects[self.currentObj]['object'].properties[key])
                    value.grid(column=0, row=row, sticky='w')
                    self.prop_right_frame.rowconfigure(row, minsize=21)

                
                    # label.config(height=value.winfo_height)

                    row += 1
            self.prop_canvas.itemconfig(self.prop_buttons, height=(row+1) * 21)
            self.prop_frame.config(height=(row+1) * 21)
            self.prop_canvas.configure(scrollregion=(0,0,500,self.prop_frame.winfo_height()))

        else:
            print('no obj')
            self.prop_canvas.itemconfig(self.prop_buttons, height=0)
            self.prop_frame.config(height=0)
            self.prop_canvas.configure(scrollregion=(0,0,500,0))

    def update_current_obj(self):
        self.level_canvas.itemconfig(self.objects[self.currentObj]['image'])


    def open_png(self):
        path = filedialog.askopenfilename(title='Open level image', defaultextension="*.png", filetypes=(('wmw level', '*.png'),('any', '*.*')), initialdir=self.gamedir+'assets/Levels')
        self.open_level_img(path)

    def open_xml(self):
        path = filedialog.askopenfilename(title='Open level XML', defaultextension="*.xml", filetypes=(('wmw level', '*.xml'),('any', '*.*')), initialdir=self.gamedir+'assets/Levels')
        # print(path)
        if path != '' and path != None:
            dialog = popups.load_dialog(self)
            # dialog.run(command=self.open_level_xml, args=(self, path, dialog))

            self.active = False

            self.open_level_xml(path, dialog)

            # thread = Thread(target=self.open_level_xml, args=(path, dialog))
            # thread.start()

            # dialog.close()

    def open_level_img(self, path=None):
        try:
            self.level_img_index
        except:
            self.level_img_index = self.level_canvas.create_image(0,0, image=None, anchor='nw')

        if path != None:
            image = Image.open(path)
        else:
            image = Image.new('P', (90,120), 255)

        image = image.resize((image.width*self.scale, image.height*self.scale), Image.Resampling.NEAREST)

        self.level_img = ImageTk.PhotoImage(image=image)
        self.level_size = (image.width, image.height)

        self.level_canvas.itemconfig(self.level_img_index, image=self.level_img)

    def open_level_xml(self, path, dialog=None):
        with open(path) as file:
            self.level_xml = file.read()
            xml = etree.fromstring(self.level_xml)
            print(xml)


        global images
        self.objects = []
        images = []

        root = xml

        if dialog:
            dialog.bar['max'] = len(root)
        
        for obj in range(len(root)):
            if dialog:
                dialog.bar['value'] = obj
                dialog.window.update()

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
        
        self.active = True
        if dialog:
            dialog.close()

    def truePos(self, pos, size=None, anchor='CENTER'):
        def error(value):
            raise NameError('anchor: ' + str(value) + ' is not valid')

        x,y = pos
        
        x *= 1 * self.scale
        y *= -1 * self.scale

        x = x + (self.level_size[0] / 2)
        y = y + (self.level_size[1] / 2)

        if size != None:
            x = x - (size[0] / (2 if anchor in ['CENTER', 'C', 'N', 'S'] else (1 if anchor in ['NE', 'E', 'SE'] else (size[0] if anchor in ['NW', 'W', 'SW'] else error(anchor)))))
            y = y - (size[1] / (2 if anchor in ['CENTER', 'C', 'W', 'E'] else (1 if anchor in ['SW', 'S', 'SE'] else (size[1] if anchor in ['NW', 'N', 'NW'] else error(anchor)))))

        return (x,y)

    def gamePos(self, pos):
        x,y = pos

        x = x - (self.level_size[0] / 2)
        y = y - (self.level_size[1] / 2)

        x = x / self.scale
        y = y / self.scale

        return (x,y)

    def addObj(self, path, pos=(0,0), properties={}):

        obj = newObject(path,pos=pos, properties=properties)
        # newPos = self.truePos(pos)
        newPos = self.truePos(pos, size=obj.size, anchor='NW')
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

    def objAt(self, pos):
        obj = next((self.objects.index(obj) for obj in self.objects[::-1] if (pos[0] >= self.level_canvas.coords(obj['image'])[0] - (obj['size'][0] / 2) and pos[0] <= int(self.level_canvas.coords(obj['image'])[0]) + int(obj['size'][0]) / 2) and (pos[1] >= self.level_canvas.coords(obj['image'])[1] - (obj['size'][1] / 2) and pos[1] <= int(self.level_canvas.coords(obj['image'])[1]) + int(obj['size'][1]) / 2)), None)
        # print(obj)
        return obj

    def moveObj(self, event):
        if not self.mouseDown:
            # self.currentObj = next((self.objects.index(obj) for obj in self.objects[::-1] if (event.x >= self.level_canvas.coords(obj['image'])[0] - (obj['size'][0] / 2) and event.x <= int(self.level_canvas.coords(obj['image'])[0]) + int(obj['size'][0]) / 2) and (event.y >= self.level_canvas.coords(obj['image'])[1] - (obj['size'][1] / 2) and event.y <= int(self.level_canvas.coords(obj['image'])[1]) + int(obj['size'][1]) / 2)), None)
            self.currentObj = self.objAt((event.x, event.y))
            print(self.currentObj)
            self.prevMousePos = (event.x, event.y)

            self.updateProps()
        
        if self.currentObj != None:
            self.level_canvas.move(self.objects[self.currentObj]['image'], event.x - self.prevMousePos[0], event.y - self.prevMousePos[1])
            self.objects[self.currentObj]['object'].pos = self.gamePos(self.level_canvas.coords(self.objects[self.currentObj]['image']))
            print(self.objects[self.currentObj]['object'].pos)
            print(self.currentObj)

            self.prevMousePos = (event.x, event.y)
        
        self.mouseDown = True


    def mouseUp(self, e=None):
        # self.currentObj = None
        self.prevMousePos = None
        self.mouseDown = False
        print(self.currentObj)

    def update_current_obj(self) -> True:
        props = {}

        for key in self.current_props:
            props[key] = self.current_props[key].get()

        angle = float(props['Angle'])

        self.objects[self.currentObj]['object'].properties = props
        self.objects[self.currentObj]['object'].update()

        images[self.currentObj] = ImageTk.PhotoImage(self.objects[self.currentObj]['object'].image.rotate(angle, expand=True))
        
        self.level_canvas.itemconfig(self.objects[self.currentObj]['image'], image=images[self.currentObj])

        # self.objects[self.currentObj]['object'].properties['Angle'] = props['Angle']

        self.updateProps()

        return True

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
