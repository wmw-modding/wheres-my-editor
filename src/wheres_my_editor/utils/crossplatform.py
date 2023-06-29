import platform
import subprocess
import os
import typing
from tkinter import ttk
import tkinter.font as tkFont
import tkmacosx


def Button(*args, system : typing.Literal['mac', 'windows', 'linux'] = None, **kwargs) -> ttk.Button:
    if isinstance(system, str):
        system = system.lower()
    else:
        system = None

    if platform.system() == 'Darwin' or system in ['mac', 'macos', 'darwin']:
        if 'width' in kwargs:
            style = ttk.Style()
            try:
                font = style.lookup(kwargs.get('style', 'TButton'), 'font')
                font = tkFont.nametofont(font)
            except:
                font = tkFont.nametofont('TkDefaultFont')
            
            width = font.measure('0')
            
            kwargs['width'] *= width * 2

        return tkmacosx.Button(*args, **kwargs)
    else:
        return ttk.Button(*args, **kwargs)

def modifier() -> typing.Literal['Control', 'Command']:
    if platform.system() == 'Darwin':
        return 'Command'
    else:
        return 'Control'

def shortModifier() -> typing.Literal['Ctrl', 'Cmd']:
    if platform.system() == 'Darwin':
        return 'Cmd'
    else:
        return 'Ctrl'

def open_file(filepath : str):
    filepath = os.path.abspath(filepath)
    
    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
    else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))
