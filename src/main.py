from email.mime import image
from tkinter.filedialog import FileDialog
import tkinter as tk
from tkinter import ttk
from guizero import *
import popups
from PIL import Image, ImageTk
from xmlviewer import XML_Viwer, autoscroll
from getObject import *
import itertools

class Window(tk.Tk):
    def __init__(self, parent):
        tk.Tk.__init__(self,parent)
        #tk.Tk.iconbitmap(self, default = 'assets/logo.xbm')
        self.parent = parent
        self.level_canvas = tk.Canvas(parent, width=90*5, height=120*5)
        self.objects_canvas = tk.Canvas(parent, width=200, height=300)
        self.prop_canvas = tk.Canvas(parent, width=200, height=300)

        self.gamedir = 'game/wmw/'
        with open(self.gamedir + 'assets/Levels/_seb_test_3_mystery.xml') as file:
            self.level_xml = file.read()

        image = Image.open(self.gamedir + 'assets/Levels/_seb_test_3_mystery.png')
        image = image.resize((image.width*5, image.height*5), Image.Resampling.NEAREST)
        self.level_img = ImageTk.PhotoImage(image=image)

        self.objects = []
            
        self.initialize()
        self.title('WMW Level Editor')
        self.geometry('%dx%d' % (760 , 610) )

    def initialize(self):
        self.grid()
    
        self.level_canvas.grid(row=0, column=1, rowspan=2)
        self.objects_canvas.grid(row=0, column=0)
        self.prop_canvas.grid(row=1, column=0)

        XML_Viwer(self.objects_canvas, self.level_xml, heading_text='objects').pack()

        self.level_img_index = self.level_canvas.create_image(0,0, image=self.level_img, anchor='nw')

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
        
        fileMenu.add_command(label= 'Open', command = self.open_png)
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
        display = self.level_canvas.create_image(50, 100, anchor='nw', image=None)
        print('display: ' + str(display))
        # window = self.level_canvas.create_window(0, 0, anchor='nw', window=display)

        bomb = createObject('game/wmw/assets/Objects/bomb.hs')
        bomb.playAnimation(self, self.level_canvas, display, bomb.sprites[0].animations[1])

    def action(self):
        pass

    def open_png(self):
        path = filedialog.askopenfilename(title='Open level image', defaultextension="*.png", filetypes=(('wmw level', '*.png'),('any', '*.*')), initialdir=self.gamedir+'assets/Levels')
        self.open_level_img(path)

    def open_level_img(self, path):
        image = Image.open(path)
        image = image.resize((image.width*5, image.height*5), Image.Resampling.NEAREST)
        self.level_img = ImageTk.PhotoImage(image=image)

        self.level_canvas.itemconfig(self.level_img_index, image=self.level_img)

    

# game_dir = ''

# level_img = None
# level_dim = [90,120]
# level_scale = 4
# level_img = Image.open("game\\wmw\\assets\\Levels\\_seb_test_3_mystery.png")
# level_img = level_img.resize((level_img.width*level_scale, level_img.height*level_scale), Image.Resampling.NEAREST)
# with open('game/wmw/assets/Levels/_seb_test_3_mystery.xml') as file:
#     level_xml = file.read()

# border = 1

# def file_function():
#     print("File option")

# def edit_function():
#     print("Edit option")

# def open_png():
#     global level_img, level, level_canvas, tk_level_img
#     path = filedialog.askopenfilename(title='choose video', defaultextension="*.png", filetypes=(('wmw level', '*.png'),('any', '*.*')))
#     print(path)
#     if path == '':
#         return
#     level_img = Image.open(path)
#     level_img = level_img.resize((level_img.width*level_scale, level_img.height*level_scale), Image.Resampling.NEAREST)

#     tk_level_img = ImageTk.PhotoImage(level_img)
#     level_canvas.itemconfig(level, image=tk_level_img)


# app = App(title="Hello world", layout='grid', width=200+(level_dim[0]*level_scale)+border*4, height=level_dim[1]*level_scale+border*2)
# menubar = MenuBar(app,
#                   toplevel=["File", "Edit"],
#                   options=[
#                       [ ["open png", open_png], ['open with selector', file_function], ["save", file_function], ['export xml', file_function], ['export png', file_function] ],
#                       [ ["Edit option 1", edit_function], ["Edit option 2", edit_function] ]
                      
#                   ])

# button = PushButton(app, text="Press me", align=)
# objects = Canvas(width=200, height=300)
# objects = tk.Canvas(highlightthickness=border, highlightbackground='black')
# img = tk.PhotoImage(file="C:\\Users\\christineka\\Pictures\\Super Mario Maker v.6 New Logo.png")
# objects.create_image(0,0, image=img)
# objects.create_text(50,50, text='this is a test', fill="black")

# XML_Viwer(objects, level_xml, heading_text="objects").pack()

# app.add_tk_widget(objects, grid=[0,0], width=200, height=300)

# properties = tk.Canvas()

# level_canvas = tk.Canvas(highlightthickness=border, highlightbackground='black')

# tk_level_img = ImageTk.PhotoImage(level_img)
# level = level_canvas.create_image(0, 0, anchor='nw', image=tk_level_img)
# print('level: ' + str(level))

# app.add_tk_widget(level_canvas, grid=[1,0,1,2], width=level_dim[0]*level_scale, height=level_dim[1]*level_scale)

# # animation viewer

# bomb = getObject('game/wmw/assets/Objects/balloon.hs')

# no_of_frames = len(bomb.sprites[0].animations[0].frames)
# duration = float(bomb.sprites[0].animations[0].fps)
# duration = int(duration)*10

# frame_list = bomb.sprites[0].animations[0].frames

# tkframe_list = [ImageTk.PhotoImage(image=fr.image) for fr in frame_list]
# tkframe_sequence = itertools.cycle(tkframe_list)
# tkframe_iterator = iter(tkframe_list)

# object_viewer = tk.Canvas(highlightthickness=border, highlightbackground='black')
# display = level_canvas.create_image(0, 0, anchor='nw', image=tkframe_list[0])
# print('display: ' + str(display))
# window = level_canvas.create_window(0, 0, anchor='nw', window=display)

# def show_animation():
#     global after_id
#     after_id = app.tk.after(duration, show_animation)
#     img = next(tkframe_sequence)
#     level_canvas.itemconfig(display, image=img)

# def stop_animation(*event):
#     app.tk.after_cancel(after_id)

# def run_animation_once():
#     global after_id
#     after_id = app.tk.after(duration, run_animation_once)
#     try:
#         img = next(tkframe_iterator)
#     except StopIteration:
#         stop_animation()
#     else:
#         level_canvas.itemconfig(display, image=img)

# app.after(0, show_animation)

# app.add_tk_widget(object_viewer, grid=[0,1])

# picture = Picture(level, image=level_img)
# prop = Text(properties, 'properties')
# obj = Text(objects, 'objects')

def main():
    # app.display()
    app = Window(None)
    app.mainloop()

if(__name__ == '__main__'):
    main()
