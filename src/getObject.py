import lxml
from lxml import etree
import os
from PIL import Image
import time

def getObject(path):
    def findTag(root, tag):
        element = 0
        curTag = ''

        for e in range(len(root)):
            print(root[e].tag)
            curTag = root[e].tag
            if curTag == tag:
                return e
                break

        return e

    def getImage(spritePath):
        def findInImagelist(path, name):
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

            sheet = Image.open(assets + sheet_info['file'])

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
            
            image.show()
            print('done')

        # assets = os.path.dirname(os.path.dirname(spritePath))
        
        with open(spritePath) as file:
            xml = etree.parse(file)
            tree = xml.getroot()
        
        print(len(tree))
        print(tree.tag)
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

            for f in frames:
                findInImagelist(assets + info['atlas'], f['name'])

        


    with open(path) as file:
        xml = etree.parse(file)
    assets = os.path.dirname(os.path.dirname(path))
    tree = xml.getroot()

    # image, properies, name, filename

    elmt = findTag(tree, 'Sprites')
    
    sprites = []

    for e in tree[elmt]:
        sprite = {}
        sprite['filename'] = e.get('filename')
        sprite['pos'] = e.get('pos')
        sprite['angle'] = e.get('angle')
        sprite['gridsize'] = e.get('gridsize')
        sprite['isBackground'] = e.get('isBackground') == 'true'

        sprites.append(sprite)

    for s in sprites:
        getImage(assets + s['filename'])

    
if __name__ == '__main__':
    getObject('/game/wmw/assets/balloon.hs')