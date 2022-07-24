import lxml
from lxml import etree
import os
from PIL import Image, ImageTk
import time
import itertools

class newObject():
    def __init__(self, path, pos=(0.0)):
        with open(path) as file:
            xml = etree.parse(file)
        assets = os.path.dirname(os.path.dirname(path))
        tree = xml.getroot()

        elmt = findTag(tree, 'Sprites')
    
        self.sprites = []

        for e in tree[elmt]:
            sprite = {}
            sprite['filename'] = e.get('filename')
            sprite['pos'] = e.get('pos')
            sprite['angle'] = e.get('angle')
            sprite['gridSize'] = e.get('gridSize')
            sprite['isBackground'] = e.get('isBackground') == 'true'
            sprite['visible'] = e.get('visible') == 'true' or e.get('visible') == None

            sprite_obj = self.sprite(assets + sprite['filename'], sprite)

            self.sprites.append(sprite_obj)

        images = []

        background = None
        
        for s in self.sprites:
            if s.isBackground:
                background = s
            if s.visible:
                pass
            images.append(s)

        if background == None:
            background = images[0]
            # del images[0]

        self.image = background.animations[0].frames[0].image.copy()
        for i in images:
            print(i.gridSize[0])
            self.image.paste(i.animations[0].frames[0].image, i.pos, i.animations[0].frames[0].image)

        # self.image.show()

        self.properties = {}
        prop = tree[findTag(tree, 'DefaultProperties')]
        for p in prop:
            self.properties[p.get('name')] = p.get('value')

        self.pos = pos


    class sprite():
        def __init__(self, path, properties) -> None:
            self.assets = os.path.dirname(os.path.dirname(path))
            with open(path) as file:
                xml = etree.parse(file)
                tree = xml.getroot()

            print(len(tree))
            print(tree.tag)
            self.animations = []
            for animation_element in tree:
                print(animation_element)

                info = {}

                info['name'] = animation_element.get('name')
                info['textureBasePath'] = animation_element.get('textureBasePath')
                info['atlas'] = animation_element.get('atlas')
                info['fps'] = animation_element.get('fps')
                info['playbackMode'] = animation_element.get('playbackMode')
                info['loopCount'] = animation_element.get('loopCount')

                frames = []

                for f in animation_element:
                    frame = {}
                    frame['name'] = f.get('name')
                    frames.append(frame)

                for f in range(len(frames)):
                    frames[f] = self.findInImagelist(self.assets + info['atlas'], frames[f]['name'])

                self.animations.append(self.animation(frames, info))

                print(properties)
                self.filename = properties['filename']
                pos = properties['pos'].split()
                self.pos = (int(float(pos[0])*10),int(float(pos[1])*10))
                self.angle = float(properties['angle'])
                gridSize = properties['gridSize'].split()
                self.gridSize = (float(gridSize[0]), float(gridSize[1]))
                # self.gridSize = properties['gridSize']
                self.isBackground = properties['isBackground']
                self.visible = properties['visible']
                print(self.pos,self.angle,self.gridSize,self.isBackground,self.visible)
        
        def findInImagelist(self, path, name):
            with open(path) as file:
                xml = etree.parse(file)
                tree = xml.getroot()

            imageList = tree
            
            sheet_info = {}
            sheet_info['imgSize'] = imageList.get('imgSize')
            sheet_info['file'] = imageList.get('file')
            sheet_info['textureBasePath'] = imageList.get('textureBasePath')

            print(len(imageList))
            for i in imageList:
                print(i.get('name'))
                if i.get('name') == name:
                    image = i
                    break

            image_info = {}
            image_info['name'] = image.get('name')
            image_info['offset'] = image.get('offset')
            image_info['size'] = image.get('size')
            image_info['rect'] = image.get('rect')

            sheet = Image.open(self.assets + sheet_info['file'])

            left, up, right, down = image_info['rect'].split()
            left = int(left)
            up = int(up)
            right = int(right)
            down = int(down)
            right = left + right
            down = up + down
            print(left, right, up, down)

            image = sheet.crop((left, up, right, down))
            x,y = image_info['size'].split()
            x = int(x)
            y = int(y)
            # image = image.resize((x,y))
            
            # image.show()
            print('got frame ' + image_info['name'])

            return self.frame(image, image_info)

        class frame():
            def __init__(self, image, properties) -> None:
                self.name = properties['name']

                self.image = image

                offset = properties['offset'].split()
                x = int(offset[0])
                y = int(offset[1])

                self.offset = [x,y]

                newsize = properties['size'].split()
                w = int(newsize[0])
                h = int(newsize[1])

                self.size = [w,h]

                left, up, right, down = properties['rect'].split()
                left = int(left)
                up = int(up)
                right = int(right)
                down = int(down)
                right = left + right
                down = up + down

                self.rect = [left, up, right, down]

        class animation():
            def __init__(self, frames, properties) -> None:
                self.frames = frames
                self.name = properties['name']
                self.textureBasePath = properties['textureBasePath']
                self.atlas = properties['atlas']
                self.fps = properties['fps']
                self.playbackMode = properties['playbackMode']
                self.loopCount = properties['loopCount']

    def playAnimation(self, app, root, display, animation):
        no_of_frames = len(animation.frames)
        duration = float(animation.fps)
        duration = int(duration)*10

        frame_list = animation.frames

        tkframe_list = [ImageTk.PhotoImage(image=fr.image) for fr in frame_list]
        tkframe_sequence = itertools.cycle(tkframe_list)
        tkframe_iterator = iter(tkframe_list)

        # object_viewer = tk.Canvas(highlightthickness=border, highlightbackground='black')
        # display = level_canvas.create_image(0, 0, anchor='nw', image=tkframe_list[0])
        # print('display: ' + str(display))
        # window = level_canvas.create_window(0, 0, anchor='nw', window=display)

        def show_animation():
            global after_id
            after_id = app.after(duration, show_animation)
            img = next(tkframe_sequence)
            self.image = img
            root.itemconfig(display, image=self.image)

        def stop_animation(*event):
            app.after_cancel(after_id)

        def run_animation_once():
            global after_id
            after_id = app.after(duration, run_animation_once)
            try:
                img = next(tkframe_iterator)
            except StopIteration:
                stop_animation()
            else:
                self.image = img
                root.itemconfig(display, image=self.image)

        app.after(0, show_animation)

def findTag(root, tag):
    element = 0
    curTag = ''
    for e in range(len(root)):
        print(root[e].tag)
        curTag = root[e].tag
        if curTag == tag:
            return e
            break

if __name__ == '__main__':
    print(newObject('game/wmw/assets/Objects/shower_head.hs'))