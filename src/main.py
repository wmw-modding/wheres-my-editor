from threading import Thread
from tkinter.filedialog import FileDialog
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from guizero import *
import popups
from PIL import Image, ImageTk
from xmlviewer import *
import getObject as getObj
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

        self.selection_rect = None

        self.style = ttk.Style()

        
        self.loadSettings()

        self.active = True

        # image = Image.open(self.gamedir + 'assets/Levels/_seb_test_3_mystery.png')
        # image = image.resize((image.width*self.scale, image.height*self.scale), Image.Resampling.NEAREST)
        # self.level_img = ImageTk.PhotoImage(image=image)

        self.objects = []
        self.currentObj = None
        self.room = {'pos':(0,0)}
        self.level_properties = {}
            
        self.initialize()

        self.title("Where's my Editor")
        self.geometry('%dx%d' % (760 , 610) )

    def initialize(self):
        self.grid()
    
        # self.level_canvas.grid(row=0, column=2, rowspan=2)
        # self.side_pane.grid(row=0, column=0, rowspan=2)
        # self.objects_canvas.grid(row=0, column=0)
        # self.prop_canvas.grid(row=1, column=0)
        # self.level_xml = '<root></root>'
        self.level_size = (90 * self.scale, 120 * self.scale)


        if self.settings['default_level']['image'] != '':
            self.open_level_img(self.settings['default_level']['image'])
        else:
            self.open_level_img()

        if self.settings['default_level']['xml'] != '':
            self.open_level_xml(self.settings['default_level']['xml'])
            # with open(self.settings['default_level']['xml']) as file:
                # self.level_xml = file.read()


        self.selector = ttk.Treeview(self.objects_canvas, show='tree')
        self.selector.pack()
        # self.selector
        # self.objects_canvas.bind('<Configure>', lambda e: self.selector.config(height=e.height))

        def update_selector(width):
            # print(self.selector.attributeList)
            # self.selector.column(1, width=width)
            pass

        self.selector.insert('','end',text='test')

        self.objects_canvas.bind('<Configure>', lambda e: update_selector(e.width))
        print(self.selector.winfo_width)
        self.selector.winfo_width = 500
        
        
        # self.xml_viewer = XML_Viwer(self.objects_canvas, self.level_xml, heading_text='objects').pack()
        # print(self.xml_viewer)
        # time.sleep(2)

        self.level_scrollbars = []
        self.level_scrollbars.append(ttk.Scrollbar(self.level_canvas, orient='vertical', command=self.level_canvas.yview))
        self.level_scrollbars[0].pack(side='right', fill='both')

        self.level_scrollbars.append(ttk.Scrollbar(self.level_canvas, orient='horizontal', command=self.level_canvas.xview))
        self.level_scrollbars[1].pack(side='bottom', fill='both')

        self.level_canvas.config(yscrollcommand=self.level_scrollbars[0].set)
        self.level_canvas.config(xscrollcommand=self.level_scrollbars[1].set)

        self.update_level_scroll()

        self.level_canvas.bind('<MouseWheel>', lambda e: self.level_scroll((0, e.delta/120)))
        self.level_canvas.bind('<Shift-MouseWheel>', lambda e: self.level_scroll((e.delta/120, 0)))

        # self.level_img_index = self.level_canvas.create_image(0,0, image=None, anchor='nw')

        self.prop_frame = ttk.LabelFrame(self.prop_canvas, text='properties', class_='prop')

        self.prop_panedWindow = ttk.PanedWindow(self.prop_frame, orient='horizontal', class_='prop')

        self.prop_left_frame = ttk.Frame(self.prop_panedWindow, width=50, class_='prop')
        self.prop_panedWindow.add(self.prop_left_frame)

        self.prop_right_frame = ttk.Frame(self.prop_panedWindow, width=50, class_='prop')
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

        self.prop_canvas.bind_class('prop', '<MouseWheel>', lambda e: self.prop_canvas.yview_scroll(int(-1*e.delta/120), 'units'))

        
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
        fileMenu.add_separator()
        fileMenu.add_command(label='Export XML', command=self.export_xml)
        # fileMenu.add_command(label= 'Close Img', command = lambda: self.openIMG('assets/WMWmap.png'))
        # fileMenu.add_command(label= 'Exit', command = self.client_exit)
        bar.add_cascade(label= 'File', menu=fileMenu)
        
        edit = tk.Menu(bar, tearoff=0)
        # edit.add_command(label= 'Copy', command = popups.commingsoon)
        # edit.add_command(label= 'Paste', command = popups.commingsoon)
        #bar.add_cascade(label= 'Edit', menu=edit)
        
        help = tk.Menu(bar, tearoff=0)
        help.add_command(label= 'View help.txt')
        # help.add_command(label= 'About', command = popups.about_dialog)
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

        # self.level_canvas_hover = False

        # def set_hover(hover=False):
        #     self.level_canvas_hover = hover

        self.level_canvas.bind('<B1-Motion>', self.drag_obj)
        self.level_canvas.bind('<ButtonRelease-1>', self.mouseUp)
        self.level_canvas.bind('<Button-1>', self.select_obj)
        # self.level_canvas.bind('<Enter>', lambda e: self.level_canvas.focus_set())
        # self.level_canvas.bind('<Leave>', lambda e: set_hover(False))
        print('binding')
        
        self.level_canvas.bind('<Left>', lambda e: self.move_obj(self.currentObj, (-2,0)))
        self.level_canvas.bind('<Shift-Left>', lambda e: self.move_obj(self.currentObj, (-10,0)))
        self.level_canvas.bind('<Control-Left>', lambda e: self.move_obj(self.currentObj, (-1,0)))

        self.level_canvas.bind('<Right>', lambda e: self.move_obj(self.currentObj, (2,0)))
        self.level_canvas.bind('<Shift-Right>', lambda e: self.move_obj(self.currentObj, (10,0)))
        self.level_canvas.bind('<Control-Right>', lambda e: self.move_obj(self.currentObj, (1,0)))

        self.level_canvas.bind('<Up>', lambda e: self.move_obj(self.currentObj, (0,-2)))
        self.level_canvas.bind('<Shift-Up>', lambda e: self.move_obj(self.currentObj, (0,-10)))
        self.level_canvas.bind('<Control-Up>', lambda e: self.move_obj(self.currentObj, (0,-1)))

        self.level_canvas.bind('<Down>', lambda e: self.move_obj(self.currentObj, (0,2)))
        self.level_canvas.bind('<Shift-Down>', lambda e: self.move_obj(self.currentObj, (0,10)))
        self.level_canvas.bind('<Control-Down>', lambda e: self.move_obj(self.currentObj, (0,1)))


        # self.bind_all("<Button-1>", lambda event: event.widget.focus_set())
        self.bind('<KeyPress-Return>', lambda e: self.level_canvas.focus_set())

    def action(self):
        pass

    def update_level_scroll(self):
        xlist = []
        ylist = []
        for obj in self.objects:
            x,y = self.level_canvas.coords(obj['image'])
            xlist.append(x)
            ylist.append(y)

        minX = min([0] + xlist)
        minY = min([0] + ylist)
        maxX = max([self.level_size[0]] + xlist)
        maxY = max([self.level_size[1]] + ylist)

        print(f'{minX=} {minY=} {maxX=} {maxY=}')

        self.level_canvas.config(scrollregion=(minX - 200, minY - 200, maxX + 200, maxY + 200))

    def level_scroll(self, amount: tuple):
        self.level_canvas.xview_scroll(int(-1*amount[0]), 'units')
        self.level_canvas.yview_scroll(int(-1*amount[1]), 'units')

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
        def addProp(key, value, row):
            label = ttk.Label(self.prop_left_frame, text=key, class_='prop')
            label.grid(column=0, row=row, sticky='w')
            self.prop_left_frame.rowconfigure(row, minsize=21)

            props = {
                'value' : tk.StringVar(), 'entry': None
            }

            value = ttk.Entry(self.prop_right_frame, textvariable=props['value'], validate='focusout', validatecommand=self.update_current_obj, class_='prop')
            value.delete(0, 'end')
            value.insert(0, self.objects[self.currentObj]['object'].properties[key])
            value.grid(column=0, row=row, sticky='w')
            self.prop_right_frame.rowconfigure(row, minsize=21)
            props['entry'] = value

            self.current_props['properties'][key] = props

        def restrict_num(var, index, mode):
            print(var, index, mode)

        for c in self.prop_left_frame.winfo_children():
            c.destroy()

        for c in self.prop_right_frame.winfo_children():
            c.destroy()
        
        row = 0
        if self.currentObj:
            self.current_props = {
                'Name' : {'value':'', 'entry':None},
                'properties': {
                    'Angle' : {'value':tk.StringVar(), 'entry': None}
                }
            }

            print(self.objects[self.currentObj]['object'].properties)
            properties = self.objects[self.currentObj]['object'].properties

            label = ttk.Label(self.prop_left_frame, text='Angle')
            label.grid(column=0, row=row, sticky='w')
            self.prop_left_frame.rowconfigure(row, minsize=21)

            value = ttk.Spinbox(self.prop_right_frame, textvariable=self.current_props['properties']['Angle']['value'], from_=-360, to=360, validate='focusout', validatecommand=self.update_current_obj)
            value.delete(0, 'end')
            value.insert(0, self.objects[self.currentObj]['object'].properties['Angle'])
            value.grid(column=0, row=row, sticky='w')
            self.prop_right_frame.rowconfigure(row, minsize=21)

            self.current_props['properties']['Angle']['entry'] = value

            print(value)
            # value.focus_set()

            row += 1

            for key in properties:
                if not key.lower() in ['angle']:
                    # label = ttk.Label(self.prop_left_frame, text=key)
                    # label.grid(column=0, row=row, sticky='w')
                    # self.prop_left_frame.rowconfigure(row, minsize=21)

                    # self.current_props[key] = tk.StringVar()

                    # value = ttk.Entry(self.prop_right_frame, textvariable=self.current_props[key], validate='focusout', validatecommand=self.update_current_obj)
                    # value.delete(0, 'end')
                    # value.insert(0, self.objects[self.currentObj]['object'].properties[key])
                    # value.grid(column=0, row=row, sticky='w')
                    # self.prop_right_frame.rowconfigure(row, minsize=21)

                    addProp(key, value, row)

                
                    # label.config(height=value.winfo_height)

                    row += 1
            self.prop_canvas.itemconfig(self.prop_buttons, height=(row+1) * 21)
            self.prop_frame.config(height=(row+1) * 21)
            self.prop_canvas.configure(scrollregion=(0,0,500,self.prop_frame.winfo_height()))

            self.current_props['properties']['Angle']['value'].trace_add('write', callback=restrict_num)
        else:
            print('no obj')
            self.prop_canvas.itemconfig(self.prop_buttons, height=0)
            self.prop_frame.config(height=0)
            self.prop_canvas.configure(scrollregion=(0,0,500,0))

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

    def export_xml(self):
        path = filedialog.asksaveasfilename(title='Save XML', defaultextension="*.xml", filetypes=(('wmw level', '*.xml'),('any', '*.*')), initialdir=self.gamedir+'assets/Levels')
        print(path)
        if path != '' and path != None:
            self.export_level_xml(path)

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
                pos = root[obj][getObj.findTag(root[obj], 'AbsoluteLocation')].get('value').split()
                object['pos'] = (float(pos[0]), float(pos[1]))

                object['properties'] = {}
                for prop in root[obj][getObj.findTag(root[obj], 'Properties')]:
                    object['properties'][prop.get('name')] = prop.get('value')

                print(object)

                self.addObj(self.gamedir + 'assets/' + object['properties']['Filename'], pos = object['pos'], properties=object['properties'], name=object['name'])
            
            elif root[obj].tag == 'Room':
                pos = root[obj][getObj.findTag(root[obj], 'AbsoluteLocation')].get('value').split()
                self.room['pos'] = (float(pos[0]), float(pos[1]))

            elif root[obj].tag == 'Properties':
                self.level_properties = {}
                for prop in root[obj]:
                    if prop.tag == 'Property':
                        self.level_properties[prop.get('name')] = prop.get('value')
        
        self.active = True
        if dialog:
            dialog.close()

    def export_level_xml(self, path):
        print('exporting')

        root = etree.Element("Objects")

        for obj in self.objects:
            object = etree.SubElement(root, 'Object')
            object.set('name', obj['name'])

            location = etree.SubElement(object, 'AbsoluteLocation')
            pos = str(obj['object'].pos[0]) + ' ' + str(obj['object'].pos[1])
            location.set('value', pos)

            properties = etree.SubElement(object, 'Properties')

            for prop in obj['object'].properties:
                property = etree.SubElement(properties, 'Property')
                property.set('name', prop)
                property.set('value', obj['object'].properties[prop])

        room = etree.SubElement(root, 'Room')
        location = etree.SubElement(room, 'AbsoluteLocation')
        pos = str(self.room['pos'][0]) + ' ' + str(self.room['pos'][1])
        location.set('value', pos)

        level_properties = etree.SubElement(root, 'Properties')
        for prop in self.level_properties:
            property = etree.SubElement(level_properties, 'Property')
            property.set('name', prop)
            property.set('value', self.level_properties[prop])

        xml = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8', standalone=True)

        print(xml)

        with open(path, mode='wb') as file:
            file.write(xml)
            messagebox.showinfo('Success!', 'xml exported successfully')

    def truePos(self, pos, size=None, anchor='CENTER'):
        def error(value):
            raise NameError('anchor: ' + str(value) + ' is not valid')

        x,y = pos
        
        x *= 1 * (self.scale + 1)
        y *= -1 * (self.scale + 1)

        x = x + (self.level_size[0] / 2)
        y = y + (self.level_size[1] / 2)

        if size != None:
            x = x - (size[0] / (2 if anchor in ['CENTER', 'C', 'N', 'S'] else (1 if anchor in ['NE', 'E', 'SE'] else (size[0] if anchor in ['NW', 'W', 'SW'] else error(anchor)))))
            y = y - (size[1] / (2 if anchor in ['CENTER', 'C', 'W', 'E'] else (1 if anchor in ['SW', 'S', 'SE'] else (size[1] if anchor in ['NW', 'N', 'NW'] else error(anchor)))))

        return (x,y)

    def gamePos(self, pos) -> tuple:
        x,y = pos

        x = x - (self.level_size[0] / 2)
        y = y - (self.level_size[1] / 2)

        x = x / (self.scale + 1)
        y = y / (self.scale + 1)

        y = -y

        return (x,y)

    def addObj(self, path, pos=(0,0), properties={}, name='object'):
        obj = getObj.newObject(path,pos=pos, properties=properties, scale=1.4)
        # newPos = self.truePos(pos)
        newPos = self.truePos(pos, size=obj.size, anchor='NW')
        print(newPos)

        object = {}
        object['name'] = name
        object['object'] = obj
        global images
        # obj.image = obj.image.resize((obj.image.width + 5, obj.image.height + 5))
        # obj.image = obj.scale_image(1.4)
        print(properties)

        try:
            angle = float(obj.properties['Angle'])
        except:
            angle = 0

        obj.rotate_image(angle)

        img = ImageTk.PhotoImage(obj.image)

        images.append(img)
        object['size'] = obj.image.size
        print(object['size'])

        object['image'] = self.level_canvas.create_image(newPos[0], newPos[1], anchor='center', image=img)
        print(self.level_canvas.coords(object['image']))

        self.objects.append(object)

    def del_obj(self, objectIndex):
        try:
            global images
            del self.objects[objectIndex]
            del images[objectIndex]
        except:
            return

    def update_current_obj(self) -> True:
        current_focus = self.focus_get()
        print(current_focus)

        props = {}

        focus = None
        for key in self.current_props['properties']:
            props[key] = self.current_props['properties'][key]['value'].get()
            if self.current_props['properties'][key]['entry'] == current_focus:
                focus = key

        angle = float(props['Angle'])

        self.objects[self.currentObj]['object'].properties = props
        self.objects[self.currentObj]['object'].update()

        self.objects[self.currentObj]['object'].rotate_image(angle)

        images[self.currentObj] = ImageTk.PhotoImage(self.objects[self.currentObj]['object'].image)

        self.level_canvas.itemconfig(self.objects[self.currentObj]['image'], image=images[self.currentObj])

        # self.objects[self.currentObj]['object'].properties['Angle'] = props['Angle']

        self.updateProps()
        self.objects[self.currentObj]['size'] = self.objects[self.currentObj]['object'].image.size

        self.update_selection(self.currentObj)

        if focus:
            self.current_props['properties'][focus]['entry'].focus_set()
        else:
            current_focus.focus_set()

        return True

    def objAt(self, pos):
        pos = (self.level_canvas.canvasx(pos[0]), self.level_canvas.canvasy(pos[1]))
        object = self.level_canvas.find_overlapping(pos[0], pos[1], pos[0], pos[1])
        # print(f'{object=}')
        if len(object) == 0:
            object == 1
        else:
            object = object[-1]

        if object == 1 or object == self.selection_rect:
            obj = None
        else:
            obj = next((self.objects.index(obj) for obj in self.objects if obj['image'] == object), None)
        # obj = next((self.objects.index(obj) for obj in self.objects[::-1] if (pos[0] >= self.level_canvas.coords(obj['image'])[0] - (obj['size'][0] / 2) and pos[0] <= int(self.level_canvas.coords(obj['image'])[0]) + int(obj['size'][0]) / 2) and (pos[1] >= self.level_canvas.coords(obj['image'])[1] - (obj['size'][1] / 2) and pos[1] <= int(self.level_canvas.coords(obj['image'])[1]) + int(obj['size'][1]) / 2)), None)
        # print(obj)
        return obj

    def select_obj(self, event):
        self.currentObj = self.objAt((event.x, event.y))
        self.prevMousePos = (event.x, event.y)
        self.updateProps()

        self.update_selection(self.currentObj)
        self.level_canvas.focus_set()

    def update_selection(self, objectIndex):
        if self.currentObj == None:
            self.level_canvas.itemconfig(self.selection_rect, state='hidden')
        else:
            self.level_canvas.itemconfig(self.selection_rect, state='normal')
            size = self.objects[objectIndex]['size']
            pos = self.level_canvas.coords(self.objects[objectIndex]['image'])

            if self.selection_rect:
                self.level_canvas.coords(self.selection_rect, pos[0] - size[0] / 2, pos[1] - size[1] / 2, pos[0] + size[0] / 2, pos[1] + size[1] / 2)
            else:
                self.selection_rect = self.level_canvas.create_rectangle(pos[0] - size[0] / 2, pos[1] - size[1] / 2, pos[0] + size[0] / 2, pos[1] + size[1] / 2)

    def drag_obj(self, event):
        # if not self.mouseDown:
        #     # self.currentObj = next((self.objects.index(obj) for obj in self.objects[::-1] if (event.x >= self.level_canvas.coords(obj['image'])[0] - (obj['size'][0] / 2) and event.x <= int(self.level_canvas.coords(obj['image'])[0]) + int(obj['size'][0]) / 2) and (event.y >= self.level_canvas.coords(obj['image'])[1] - (obj['size'][1] / 2) and event.y <= int(self.level_canvas.coords(obj['image'])[1]) + int(obj['size'][1]) / 2)), None)
        #     self.currentObj = self.objAt((event.x, event.y))
        #     print(self.currentObj)
        #     self.prevMousePos = (event.x, event.y)

        #     self.updateProps()
        
        if self.currentObj != None:
            self.move_obj(self.currentObj, (event.x - self.prevMousePos[0], event.y - self.prevMousePos[1]))

            # self.level_canvas.move(self.objects[self.currentObj]['image'], event.x - self.prevMousePos[0], event.y - self.prevMousePos[1])
            # self.objects[self.currentObj]['object'].pos = self.gamePos(self.level_canvas.coords(self.objects[self.currentObj]['image']))
            print(self.objects[self.currentObj]['object'].pos)
            print(self.currentObj)

            self.prevMousePos = (event.x, event.y)
        
        self.mouseDown = True

    def move_obj(self, objectIndex, pos):
        print('moved')
        if pos != None:
            self.level_canvas.move(self.objects[objectIndex]['image'], pos[0], pos[1])
            self.objects[objectIndex]['object'].pos = self.gamePos(self.level_canvas.coords(self.objects[objectIndex]['image']))
            
            self.update_selection(objectIndex)
            
            print(self.objects[objectIndex]['object'].pos)
            print(objectIndex)

        self.update_level_scroll()

    def mouseUp(self, e=None):
        # self.currentObj = None
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
