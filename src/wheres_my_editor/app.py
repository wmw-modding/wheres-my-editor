import logging

from . import _log_filename
from . import log_exception
from .level_editor.level_editor import LevelEditor
from . import __min_wmwpy_version__


def main(logo = 'assets/images/WME_logo.png', app_icons : list[str] = ['assets/images/icon_256x256.ico']):
    try:
        app = LevelEditor(None, logo = logo, app_icons = app_icons)
        app.mainloop()
    except Exception as e:
        log_exception()

if(__name__ == '__main__'):
    main()
