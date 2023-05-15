import PyInstaller.__main__
import os
import sys
import time

options = [
    'src/main.py',
    '--onefile',
    '--icon=src/assets/images/new-icon_256x256.ico',
    f'--add-data=src/assets{os.pathsep}assets',
    '--name=wme',
]

debug = False

args = sys.argv
if len(args) > 1:
    if args[1] in ['-d', '--debug']:
        debug = True
        
if debug:
    options.append('--console')
else:
    options.append('--noconsole')



print(f'{options = }')
time.sleep(1)

PyInstaller.__main__.run(options)
