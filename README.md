# Where's My Editor?
<p align="center">
<img alt="Where's My Editor? logo" src="src/assets/images/WME_logo.png" width="50%" >
<br>
Logo created by rubice!
</p>
Where's My Editor? is a level editor for the mobile game, Where's My Water? and all it's spinoffs.

NOTE: If you came here to read a .waltex image, then go to [wmwpy](https://github.com/wmw-modding/wmwpy/blob/main/src/wmwpy/utils/waltex.py). `waltex.py` has moved there.

# Get started
To get started
1. Get the latest release from the [releases tab](https://github.com/wmw-modding/wheres-my-editor/releases/latest). Extract the zip folder into it's own folder (to keep it's files organized).
2. Next, you need to get the game files. You can get them in many ways, but generally, you want to have the game extracted into a folder, and all the assets in the `assets` (or `Content`) folder.
3. Open the Where's My Editor app (wme.exe)
4. Select the game folder.
5. Now you got it up and running.

If you run into any issues, please send a bug report (shortcut in **Help > Send bug report**, or the issues page in this repository).

# How to use

After you load a level, you can move around, and edit objects.

## Moving objects

You can move objects by clicking on it, and dragging it anywhere. You can also use the arrow keys for finer placement. You can also hold some modifier keys to change the amount moved

- **Shift** + **Arrow key** = 4
- **Arrow key** = 1
- **Control** (or **Command**) + **Arrow key** = 0.5
- **Alt** + **Arrow key** = 0.1

# Development
If you're going to be editing wme, you should also edit wmwpy, as wmwpy handles all the reading and writing of the wmw files.

## Setup

1. Create a folder that both wme and wmwpy can be in.

```
/
  /wheres-my-editor
  /wmwpy
```

2. Clone wme into `wheres-my-editor`

```sh
git clone https://github.com/wmw-modding/wheres-my-editor.git
```

4. Clone wmwpy into `wmwpy`

```sh
git clone https://github.com/wmw-modding/wmwpy.git
```

5. Create wme virtual environment

A virtual environment is a very good thing to use, because it allows you to keep an instance of all the installed modules without overriding your main installation.

```sh
cd wheres-my-editor
python -m venv .venv
./.venv/Scripts/activate
```

6. Install dependencies

```sh
pip install -r requirements.txt
```

7. Add local clone of wmwpy

```sh
pip install -e ../wmwpy
```

The `-e` argument is used to tell pip that you want wmwpy to be editable, aka, if you edit wmwpy from your clone, it will be updated in wme.

8. Run wme

Now you can run wme

```sh
cd src
python main.py
```

## Build exe
### Install dependencies
To build an exe for wme, you need to install the dependencies.

```sh
pip install -r requirements-build.txt
```

This will override your editable installation of wmwpy (in the venv, it will not replace your edits), so you'll have to reinstall wmwpy again.

```sh
pip install -e ../wmwpy
```

(Tip: you can also install `requirements/requirements-build.txt` to only install the build requirements)

You can also edit `requirements.txt` to add  `-e "../wmwpy"`, and then you won't have to bother with reinstalling wmwpy, but if you're going to be publishing your edits, you might want to replace it with the link to your wmwpy clone repo instead of a path to your local clone.

If you're going to be making a release, please note that the github action will install wmwpy from pypi, so you may have to edit `requirements/requirements-dist.txt` if you want to use your personal edit of wmwpy.

### Build exe

```sh
python build.py
```

The output is in `dis/wme.exe` (it won't be an exe if you're not on windows).

# Todo

- [x] Export `xml` file
- [x] Export `png` file
- [x] Add and remove objects
- [ ] Room object. 
    - This has kind of been implemented, because wmw1 uses the image for the room placement, but the later games use an object (which can be loaded).
- [ ] Complete settings menu
- [ ] Level explorer
- [x] Fix some objects not loading
- [ ] Image editor

# Credits
- Thanks to [rubice!](https://youtube.com/@rubice2022) for creating the logo. I am not skilled enough to make something that looks that good.
- Thanks to [campbellsonic](https://github.com/campbellsonic) for the script to load `waltex` images. I could not have done it without them.

# Special thanks
- Thanks to AwesomeDragon970#8068 for helping debug the program on MacOS. They are very awesome!
