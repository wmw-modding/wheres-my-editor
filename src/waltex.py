import numpy
from PIL import Image
import math
import json

def WrapRawData(rawData : bytes, width : int, height : int, bytesPerPixel : int, redBits : int, greenBits : int, blueBits : int, alphaBits : int, colorOrder : str, premultiplyAlpha : bool = False, dePremultiplyAlpha : bool = False):
    _8BIT_MASK = 256.0
    OUTBITDEPTH = 8
    DEBUG_MODE = False
    
    # width and height are switched due to how PIL creates an image from array
    # image = [[(0, 0, 0, 0)] * height] * width
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    x = 0
    y = 0
    
    redMask = GenerateBinaryMask(redBits)
    greenMask = GenerateBinaryMask(greenBits)
    blueMask = GenerateBinaryMask(blueBits)
    alphaMask = GenerateBinaryMask(alphaBits)
    
    redMax = math.pow(2, redBits)
    greenMax = math.pow(2, greenBits)
    blueMax = math.pow(2, blueBits)
    alphaMax = math.pow(2, alphaBits)
    
    # determine number of loops needed to get every pixel
    numLoops = int(len(rawData) / bytesPerPixel)
    
    # loop for each set of bytes (one pixel)
    for i in range(numLoops):
        pixel = 0
        
        # read all bytes for this pixel
        for j in range(bytesPerPixel):
            nextByte = rawData[i * bytesPerPixel + j]
            
            # print(f'Read byte: {hex(nextByte)}')
            
            # move the byte up
            # if (reverseBytes)
            nextByte = nextByte << (8 * j)
            # else
            # pixel = pixel << 8
            
            # append the next one
            pixel += nextByte
            # print(f'Pixel is now: {hex(pixel)}')
            
        # print(f'Pixel: {pixel}')
        
        # get RGBA values from the pixel
        r, g, b, a, = 0, 0, 0, 0
        
        # loop for each channel
        for j in reversed(range(len(colorOrder))):
            color = colorOrder[j]
            
            if color == 'r':
                r = pixel & redMask
                pixel = pixel >> redBits
                
            elif color == 'g':
                g = pixel & greenMask
                pixel = pixel >> greenBits
            
            elif color == 'b':
                b = pixel & blueMask
                pixel = pixel >> blueBits
                
            else:
                a = pixel & alphaMask
                pixel = pixel >> alphaBits
                
        # print(f'Before scale:\nR: {r} G: {g} B: {b} A: {a}')
        
        # scale colors to 8-bit depth (not sure which method is better)
        
        # via floating point division
        # if (redMax > 1):
        #     r = round(r * ((_8BIT_MASK - 1) / (redMax - 1)))
        # if (greenMax > 1):
        #     g = round(g * ((_8BIT_MASK - 1) / (greenMax - 1)))
        # if (blueMax > 1):
        #     b = round(b * ((_8BIT_MASK - 1) / (blueMax - 1)))
        # if (alphaMax > 1):
        #     a = round(a * ((_8BIT_MASK - 1) / (alphaMax - 1)))
        
        # via bit shifting
        rShift = OUTBITDEPTH - redBits
        gShift = OUTBITDEPTH - greenBits
        bShift = OUTBITDEPTH - blueBits
        aShift = OUTBITDEPTH - alphaBits
        r = (r << rShift) + (r >> (redBits - rShift))
        g = (g << gShift) + (r >> (greenBits - gShift))
        b = (b << bShift) + (r >> (blueBits - bShift))
        a = (a << aShift) + (a >> (alphaBits - aShift))
        
        # print(f'After scale:\nR: {r} G: {g} B: {b} A: {a}')
        
        # if there are no bits allotted for an alpha channel, make pixel opaque rather than invisible
        if alphaBits == 0:
            a = 255
            
        # a = 255
            
        if premultiplyAlpha:
            r = round(r * a / 255.0)
            g = round(g * a / 255.0)
            b = round(b * a / 255.0)
            
        if dePremultiplyAlpha:
            if (a != 0):
                r = round(r * 255.0 / a)
                g = round(g * 255.0 / a)
                b = round(b * 255.0 / a)
            
        # set the pixel
        rgba = (int(r), int(g), int(b), int(a))
        # print(rgba)
        # image[x][y] = rgba
        image.putpixel((x,y), rgba)
        
        # break after first pixel if in debug mode
        
        
        # iterate coordinates
        x += 1
        if (x == width):
            x = 0
            y += 1
            if (y > (height - 300) or y % 100 == 0):
                print(f'Line {y} of {height} done')
                if (DEBUG_MODE):
                    break
                
        # if there's extra data (like the door overlays in the lawns), stop once the height is reached
        if y == height:
            break
        
    
    return image

def GenerateBinaryMask(numOnes):
    binaryMask = 0
    for i in range(numOnes):
        binaryMask *= 2
        binaryMask += 1
        
    return binaryMask

if __name__ == "__main__":
    path = "Carl.waltex"
    with open(path, 'rb') as file:
        rawData = file.read()
        
    image = WrapRawData(rawData, 1024, 1024, 2, 4, 4, 4, 4, 'rgba', dePremultiplyAlpha=True)
    # print(image)
    image.show()
    
    # with open('pixels.json', 'w') as file:
    #     json.dump(image, file)
        
    # pixels = numpy.array(image, dtype=numpy.uint8)
    # pixels = pixels.astype('uint8')
    # print(pixels)
    # new_image = Image.fromarray(pixels, 'RGBA')
    # new_image = Image.new('RGBA', (1024, 1024))
    # flattened = list(pixels.flatten())
    # print(flattened)
    # new_image.putdata(new_image)
    # new_image.show()
