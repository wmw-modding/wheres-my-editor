import tkinter as tk
from tkinter import ttk
import typing
import logging

class EditableLabel(ttk.Label):
    def __init__(self, parent, *args, callback : typing.Callable[[str], bool] = None, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.entry = ttk.Entry(self)
        self.callback = callback
        self.bind("<Double-1>", self.edit_start)
        self.entry.bind("<Return>", self.edit_stop)
        self.entry.bind("<FocusOut>", self.edit_stop)
        self.entry.bind("<Escape>", self.edit_cancel)

    def edit_start(self, event=None):
        self.entry.delete(0, "end")
        text = self.cget("text")
        self.entry.insert(0, text)
        self.entry.place(relx=.5, rely=.5, relwidth=1.0, relheight=1.0, anchor="center")
        self.entry.focus_set()
        
        self.editing = True

    def edit_stop(self, event=None):
        if not self.editing:
            return
        self.editing = False
        
        text = self.entry.get()
        result = True
        if self.callback:
            logging.debug('callback')
            result = self.callback(text)
        
        if result:
            try:
                self.configure(text=text)
                self.entry.place_forget()
            except:
                pass
        else:
            self.edit_start()
        

    def edit_cancel(self, event=None):
        self.entry.delete(0, "end")
        self.entry.place_forget()
