import platform
import typing
from tkinter import ttk
import tkmacosx


def Button(*args, system : typing.Literal['mac', 'window', 'linux'] = None, **kwargs) -> ttk.Button:
    if isinstance(system, str):
        system = system.lower()
    else:
        system = None

    if platform.system() == 'Darwin' or system in ['mac', 'macos', 'darwin']:
        if 'width' in kwargs:
            kwargs['width'] *= 10

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
