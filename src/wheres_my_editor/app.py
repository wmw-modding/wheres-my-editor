import logging

from . import __min_wmwpy_version__
from . import _log_filename
from .level_editor.level_editor import LevelEditor
from .utils.settings import Settings

import tkinter as tk
from tkinter import ttk

class WME(tk.Tk):
    def __init__(self, parent, **args) -> None:
        super().__init__(parent)
        self.parent = parent

        self.settings_version = 3

        self.settings = Settings(
            filename = 'settings.json',
            default_settings = {
                'version': self.settings_version,
                'game': {
                    'gamepath': '',
                    'assets': '/assets',
                    'game': 'wmw',
                }
            }
        )
        self.update_settings()

        self.levelEditor = LevelEditor(None)


    def update_settings(self):
        version = self.settings.get('version')

        try:
            gamedir = self.settings.get('gamedir')
            self.settings.set('game.gamepath', gamedir)
            self.settings.remove('gamedir')
        except:
            pass
        try:
            default_level = self.settings.get('default_level')
            self.settings.set('level_editor.default_level', default_level)
            self.settings.remove('default_level')
            self.settings.set('level_editor.version', 3)
        except:
            try:
                default_level = self.settings.get('game.default_level')
                self.settings.set('level_editor.default_level', default_level)
                self.settings.remove('game.default_level')
                self.settings.set('level_editor.version', 3)
            except:
                pass

        if version != self.settings_version:
            self.settings.set('version', self.settings_version)

def main(logo = 'assets/images/WME_logo.png', app_icons : list[str] = ['assets/images/icon_256x256.ico']):
    try:
        app = WME(None, logo = logo, app_icons = app_icons)
        app.mainloop()
    except Exception as e:
        logging.exception('app error:')

if(__name__ == '__main__'):
    main()
