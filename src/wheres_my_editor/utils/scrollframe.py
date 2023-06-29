# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Code was created by @mp035 https://gist.github.com/mp035/9f2027c3ef9172264532fcd6262f3b01
# The onMouseWheel function was modified to use an improvement by @adam-jw-casey https://gist.github.com/mp035/9f2027c3ef9172264532fcd6262f3b01?permalink_comment_id=4512797#gistcomment-4512797

import platform
import tkinter as tk
from tkinter import ttk


# ************************
# Scrollable Frame Class
# ************************
class ScrollFrame(ttk.Frame):
    def __init__(self, parent, background = '#ffffff', borderwidth = 0, usettk = False, **kwargs):
        super().__init__(parent, **kwargs) # create a frame (self)

        if usettk:
            background = ttk.Style().lookup("TFrame", "background", default="white")
        
        self.canvas = tk.Canvas(self, borderwidth = borderwidth, background=background, **kwargs)          #place canvas on self
        if usettk:
            self.viewPort = tk.Frame(self.canvas, background=background)                    #place a frame on the canvas, this frame will hold the child widgets 
            self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        else:
            self.viewPort = ttk.Frame(self.canvas)                    #place a frame on the canvas, this frame will hold the child widgets 
            self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview) #place a scrollbar on self 
        
        self.canvas.configure(yscrollcommand=self.vsb.set)                          #attach scrollbar action to scroll of canvas

        self.vsb.pack(side="right", fill="y")                                       #pack scrollbar to right of self
        self.canvas.pack(side="left", fill="both", expand=True)                     #pack canvas to left of self and expand to fil
        self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw",            #add view port frame to canvas
                                  tags="self.viewPort")

        self.viewPort.bind("<Configure>", self.onFrameConfigure)                       #bind an event whenever the size of the viewPort frame changes.
        self.canvas.bind("<Configure>", self.onCanvasConfigure)                       #bind an event whenever the size of the canvas frame changes.

        self.viewPort.bind('<Enter>', self.onEnter)                                 # bind wheel events when the cursor enters the control
        self.viewPort.bind('<Leave>', self.onLeave)                                 # unbind wheel events when the cursorl leaves the control

        self.onFrameConfigure(None)                                                 #perform an initial stretch on render, otherwise the scroll region has a tiny border until the first resize

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))                 #whenever the size of the frame changes, alter the scroll region respectively.

    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width = canvas_width - 2)            #whenever the size of the canvas changes alter the window region respectively.
    
    def resetCanvasScroll(self):
        self.canvas.yview_moveto(0)
        self.canvas.xview_moveto(0.5)

    def onMouseWheel(self, event: tk.Event):  # cross platform scroll wheel event
        canvas_height = self.canvas.winfo_height()
        rows_height = self.canvas.bbox("all")[3]

        if rows_height > canvas_height: # only scroll if the rows overflow the frame
            if platform.system() == 'Windows':
                self.canvas.yview_scroll(int(-1* (event.delta/120)), "units")
            elif platform.system() == 'Darwin':
                self.canvas.yview_scroll(int(-1 * event.delta), "units")
            else:
                if event.num == 4:
                    self.canvas.yview_scroll( -1, "units" )
                elif event.num == 5:
                    self.canvas.yview_scroll( 1, "units" )

    def onEnter(self, event):                                                       # bind wheel events when the cursor enters the control
        if platform.system() == 'Linux':
            self.canvas.bind_all("<Button-4>", self.onMouseWheel)
            self.canvas.bind_all("<Button-5>", self.onMouseWheel)
        else:
            self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)

    def onLeave(self, event):                                                       # unbind wheel events when the cursorl leaves the control
        if platform.system() == 'Linux':
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")
