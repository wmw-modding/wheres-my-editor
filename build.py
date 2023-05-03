import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    'src/main.pyw',
    '--onefile',
    '--windowed',
    '--icon=src/assets/images/icon.png',
    f'--add-data=src/assets{os.pathsep}assets',
    '--name=wme',
])
