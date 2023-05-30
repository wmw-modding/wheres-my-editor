import PyInstaller.__main__
import os
import sys
import time
import platform

print(f'platform: {platform.system()}')

options = [
    'src/main.py',
    '--icon=src/assets/images/icon_256x256.ico',
    f'--add-data=src/assets{os.pathsep}assets',
    '--name=wme',
    '--onefile',
]

debug = False

args = sys.argv
if len(args) > 1:
    args = args[1:]
    
    for index in range(len(args)):
        arg = args[index]
        
        if arg in ['-d', '--debug']:
            debug = True
        elif arg in ['-o', '--output']:
            options.append(f"--distpath={os.path.join('./dist', args[index + 1])}")
            options.append(f"--workpath={os.path.join('./build', args[index + 1])}")
        
if debug:
    options.append('--console')
else:
    options.append('--windowed')



print(f'{options = }')
# time.sleep(1)

PyInstaller.__main__.run(options)
