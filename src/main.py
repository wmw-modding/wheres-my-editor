from tkinter.filedialog import FileDialog
import tkinter as tk
from guizero import *
from PIL import Image, ImageTk
from xmlviewer import XML_Viwer, autoscroll

game_dir = ''

level_img = None
level_dim = [90,120]
level_scale = 4
level_img = Image.open("game\\wmw\\assets\\Levels\\_seb_test_3_mystery.png")
level_img = level_img.resize((level_img.width*level_scale, level_img.height*level_scale), Image.Resampling.NEAREST)
with open('game/wmw/assets/Levels/_seb_test_3_mystery.xml') as file:
    level_xml = file.read()

border = 1

def file_function():
    print("File option")

def edit_function():
    print("Edit option")

def open_png():
    global level_img, level, level_canvas, tk_level_img
    path = filedialog.askopenfilename(title='choose video', defaultextension="*.png", filetypes=(('wmw level', '*.png'),('any', '*.*')))
    print(path)
    if path == '':
        return
    level_img = Image.open(path)
    level_img = level_img.resize((level_img.width*level_scale, level_img.height*level_scale), Image.Resampling.NEAREST)

    tk_level_img = ImageTk.PhotoImage(level_img)
    level_canvas.itemconfig(level, image=tk_level_img)


app = App(title="Hello world", layout='grid', width=200+(level_dim[0]*level_scale)+border*4, height=level_dim[1]*level_scale+border*2)
menubar = MenuBar(app,
                  toplevel=["File", "Edit"],
                  options=[
                      [ ["open png", open_png], ['open with selector', file_function], ["save", file_function], ['export xml', file_function], ['export png', file_function] ],
                      [ ["Edit option 1", edit_function], ["Edit option 2", edit_function] ]
                      
                  ])

# button = PushButton(app, text="Press me", align=)
# objects = Canvas(width=200, height=300)
objects = tk.Canvas(highlightthickness=border, highlightbackground='black')
# img = tk.PhotoImage(file="C:\\Users\\christineka\\Pictures\\Super Mario Maker v.6 New Logo.png")
# objects.create_image(0,0, image=img)
# objects.create_text(50,50, text='this is a test', fill="black")

XML_Viwer(objects, level_xml, heading_text="objects").pack()

app.add_tk_widget(objects, grid=[0,0], width=200, height=300)

properties = tk.Canvas()

level_canvas = tk.Canvas(highlightthickness=border, highlightbackground='black')

tk_level_img = ImageTk.PhotoImage(level_img)
level = level_canvas.create_image(0, 0, anchor='nw', image=tk_level_img)

app.add_tk_widget(level_canvas, grid=[1,0], width=level_dim[0]*level_scale, height=level_dim[1]*level_scale)

# picture = Picture(level, image=level_img)
# prop = Text(properties, 'properties')
# obj = Text(objects, 'objects')

def main():
    app.display()

if(__name__ == '__main__'):
    main()
