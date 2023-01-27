import math
import lxml
from lxml import etree
import os
import itertools
from PIL import Image, ImageTk
from .waltex import getWaltexImage

walteximages = {}

class newObject():
    def __init__(self, path, pos=(0.0), properties={}, scale=1, assetpath=None):
        with open(path) as file:
            xml = etree.parse(file)

        if assetpath == None:
            self.assets = os.path.dirname(os.path.dirname(path))
        else:
            self.assets = assetpath
        tree = xml.getroot()

        elmt = findTag(tree, 'Sprites')

        self.sprites = []
        self.scale = scale

        for e in tree[elmt]:
            if e.tag == 'Sprite':
                newSprite = {}
                newSprite['filename'] = e.get('filename')
                newSprite['pos'] = e.get('pos')
                newSprite['angle'] = e.get('angle')
                newSprite['gridSize'] = e.get('gridSize')
                newSprite['isBackground'] = e.get('isBackground') == 'true'
                newSprite['visible'] = e.get('visible') == 'true' or e.get('visible') == None

                sprite_obj = sprite(self.assets + newSprite['filename'], newSprite, self.assets)

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
            try:
                self.image.paste(i.animations[0].frames[0].image, self.truePos(i.pos, self.image.size, i.animations[0].frames[0].image.size), i.animations[0].frames[0].image)
            except:
                pass

        # self.image.show()

        self.properties = {
            'Angle' : '0',
            'Filename' : '/' + os.path.relpath(path, self.assets).replace('\\', '/')
        }

        prop = tree[findTag(tree, 'DefaultProperties')]
        for p in prop:
            self.properties[p.get('name')] = p.get('value')

        for key in properties:
            self.properties[key] = properties[key]

        self._filename = self.properties['Filename']

        self._image = self.image

        self.size = self.image.size
        self.image = self.scale_image(self.scale)

        self.pos = pos

    def rotate_image(self, angle):
        self.rotation = angle

        self.image = self._image.rotate(angle, expand=True, resample=Image.BILINEAR)
        self.image = self.scale_image(self.scale)

    def update(self):
        if self._filename != self.properties['Filename']:
            self._filename = self.properties['Filename']
            self.__init__(self.assets + self._filename, properties=self.properties, pos=self.pos, scale=self.scale)
            
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

    def truePos(self, pos, source_size, image_size=None, scale=1, anchor='CENTER'):
        def error(value):
            raise NameError('anchor: ' + str(value) + ' is not valid')

        if image_size == None:
            image_size = source_size

        print(pos)
        x = pos[0] * scale
        y = pos[1] * -1 * scale

        x += source_size[0] / (2 if anchor in ['CENTER', 'C', 'N', 'S'] else (1 if anchor in ['NE', 'E', 'SE'] else (source_size[0] if anchor in ['NW', 'W', 'SW'] else error(anchor))))
        y += source_size[1] / (2 if anchor in ['CENTER', 'C', 'W', 'E'] else (1 if anchor in ['SW', 'S', 'SE'] else (source_size[1] if anchor in ['NW', 'N', 'NW'] else error(anchor))))

        x -= image_size[0] / (2 if anchor in ['CENTER', 'C', 'N', 'S'] else (1 if anchor in ['NE', 'E', 'SE'] else (image_size[0] if anchor in ['NW', 'W', 'SW'] else error(anchor))))
        y -= image_size[1] / (2 if anchor in ['CENTER', 'C', 'W', 'E'] else (1 if anchor in ['SW', 'S', 'SE'] else (image_size[1] if anchor in ['NW', 'N', 'NW'] else error(anchor))))

        x = round(x)
        y = round(y)
        
        print(x,y)

        return (x,y)

    def scale_image(self, scale):

        size = (self.image.width, self.image.height)
        aspect_ratio = size[1]/size[0]

        width = size[0] * scale
        height = width * aspect_ratio

        newSize = (math.floor(width), math.floor(height))

        return self.image.resize(newSize)

class sprite():
    def __init__(self, path, properties, assetspath) -> None:
        self.assets = assetspath
        # self.assets = os.path.dirname(os.path.dirname(path))
        print(path)
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
                frames[f] = findInImagelist(self.assets + info['atlas'], frames[f]['name'], self.assets)

            self.animations.append(animation(frames, info))

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
    
def exportImagelist(filename, assetspath):
    with open(filename, 'r') as file:
        xml = etree.parse(file)
        tree = xml.getroot()

    imageList = tree
    sheet_info = {}
    sheet_info['imgSize'] = imageList.get('imgSize')
    sheet_info['file'] = imageList.get('file')
    sheet_info['textureBasePath'] = imageList.get('textureBasePath')

    image = None
    images = []

    print(len(imageList))
    for i in imageList:
        print(i.get('name'))
        image = i
        
        image_info = {}
        image_info['name'] = image.get('name')
        image_info['offset'] = image.get('offset')
        image_info['size'] = image.get('size')
        image_info['rect'] = image.get('rect')

        sheet = Image.open(assetspath + sheet_info['file'])

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
        images.append(frame(image, image_info))
        print('got frame ' + image_info['name'])

    return images

def findInImagelist(path, name, assetspath):
    with open(path) as file:
        xml = etree.parse(file)
        tree = xml.getroot()

    imageList = tree
    
    sheet_info = {}
    sheet_info['imgSize'] = imageList.get('imgSize')
    sheet_info['file'] = imageList.get('file')
    sheet_info['textureBasePath'] = imageList.get('textureBasePath')
    
    sheet_size = sheet_info['imgSize'].split(' ')
    sheet_size = (int(sheet_size[0]), int(sheet_size[1]))

    print(name)

    image = None

    print(len(imageList))
    for i in imageList:
        print(i.get('name'))
        if i.get('name') == name:
            image = i
            break

    if image == None:
        image_info = {
            'name' : 'NO_TEX.png',
            'offset': '0 0',
            'size': '32 32',
            'rect': '0 0 32 32'
        }

        sheet = Image.open(assetspath + '/Textures/NO_TEX.png')
    else:
        image_info = {}
        image_info['name'] = image.get('name')
        image_info['offset'] = image.get('offset')
        image_info['size'] = image.get('size')
        image_info['rect'] = image.get('rect')
        
        if os.path.splitext(sheet_info['file'])[1] == '.waltex':
            try:
                sheet = walteximages[sheet_info['file']]
            except:
                settings = getTextureSettings(assetspath + os.path.dirname(os.path.dirname(sheet_info['textureBasePath'])) + '/Data/textureSettings.xml', sheet_info['file'])
                sheet = getWaltexImage(assetspath + sheet_info['file'], sheet_size, settings['colorspace'], premultiplyAlpha=settings['premultiplyAlpha'])
                
                walteximages[sheet_info['file']] = sheet
        else:
            sheet = Image.open(assetspath + sheet_info['file'])

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

    return frame(image, image_info)

def getTextureSettings(path, name):
    with open(path, 'r') as file:
        xml = etree.parse(file)
        root = xml.getroot()
        
    texture = None
    
    print(name)
        
    for element in root:
        if element.tag == 'Texture':
            print(element)
            print(element.get('name'))
            if element.get('name') in name:
                texture = element
                break
    print(texture)
            
    texturesettings = {
        'element': texture,
        'name': name,
        'colorspace': texture.get('colorspace'),
        'premultiplyAlpha': texture.get('premultiplyAlpha'),
        'alphaClip': texture.get('alphaClip'),
        'outlineColor': texture.get('outlineColor'),
        'greyTolerance': texture.get('greyTolerance'),
        'wrapU': texture.get('wrapU'),
        'wrapV': texture.get('wrapV'),
        'uncompressedExt': texture.get('uncompressedExt'),
    }
    
    return texturesettings

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
    obj = newObject('game/wmw/assets/Objects/star.hs')
    room = findInImagelist('game/wmw/assets/Textures/objects.imagelist', 'Portal_Exterior.png', 'game/wmw/assets/')
    # print(obj, obj.truePos((0,2), obj.image.size, anchor='d'))
    room.image.show()
    obj.image.show()
