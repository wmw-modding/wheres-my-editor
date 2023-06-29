__version__ = '3.0.0'
__author__ = 'ego-lay-atman-bay'
__credits__ = [
    {
        'name' : 'wmwpy',
        'url' : 'https://github.com/wmw-modding/wmwpy',
        'description' : "Where's My Editor? uses wmwpy to read and modify Where's My Water? data, e.g. levels."
    },
    {
        'name' : 'rubice!',
        'url' : 'https://www.youtube.com/channel/UCsY-c5mJYWnK6PhrkHqPwig',
        'description' : 'Thanks to @rubice for creating the logo.'
    },
    {
        'name' : 'campbellsonic',
        'url' : 'https://github.com/campbellsonic',
        'description' : 'Thanks to @campbellsonic for helping to read waltex images.'
    }
]
__links__ = {
    'discord' : 'https://discord.gg/eRVfbgwNku',
    'releases' : 'https://github.com/wmw-modding/wheres-my-editor/releases/latest',
    'bugs' : 'https://github.com/wmw-modding/wheres-my-editor/issues',
}
__min_wmwpy_version__ = "0.5.0-beta"


from datetime import datetime
import io
import logging
import os
import traceback


def createLogger(type = 'file', filename = 'logs/log.log'):
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    format = '[%(levelname)s] %(message)s'
    datefmt = '%I:%M:%S %p'
    level = logging.DEBUG

    # filename = 'log.log'

    handlers = []

    if type == 'file':
        try:
            os.mkdir('logs')
        except:
            pass

        handlers.append(logging.FileHandler(filename))
        format = '[%(asctime)s] [%(levelname)s] %(message)s'

        # logging.basicConfig(filename=filename, filemode='w', format=format, datefmt=datefmt, level=level)
        # logger.info('logging file')

    handlers.append(logging.StreamHandler())
    logging.basicConfig(format=format, datefmt=datefmt, level=level, handlers=handlers)

    logger = logging.getLogger(__name__)
    logger.info(filename)


_log_filename = f'logs/{datetime.now().strftime("%m-%d-%y_%H-%M-%S")}.log'

createLogger('file', filename = _log_filename)


def log_exception():
    fileio = io.StringIO()
    traceback.print_exc(file = fileio)

    logging.error(fileio.getvalue())


import wmwpy

if wmwpy.__version__ < __min_wmwpy_version__:
    logging.error(f'wmwpy version must be "{__min_wmwpy_version__}" or higher.')
    raise ImportWarning(f'wmwpy version must be "{__min_wmwpy_version__}" or higher.')

from PIL import ImageColor

ImageColor.colormap['transparent'] = '#0000'



import tkinter as tk

class TkErrorCatcher:

    '''
    In some cases tkinter will only print the traceback.
    Enables the program to catch tkinter errors and log them.
    To use
    import tkinter
    tkinter.CallWrapper = TkErrorCatcher
    '''

    def __init__(self, func, subst, widget):
        self.func = func
        self.subst = subst
        self.widget = widget

    def __call__(self, *args):
        try:
            if self.subst:
                args = self.subst(*args)
            return self.func(*args)
        except SystemExit as msg:
            raise SystemExit(msg)
        except Exception as e:
            log_exception()

tk.CallWrapper = TkErrorCatcher
