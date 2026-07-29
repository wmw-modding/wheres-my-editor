from PIL import Image

class Icicle:
    def icicle_corner_left(sprite, filename, sprite_image, sprite_pos, sprite_size, glow_name, wmw2=False):
        if 'filename' in sprite.properties:
            filename = sprite.properties['filename']
            if glow_name in filename.lower():
                sprite_image = sprite.image.rotate(180, resample = Image.BILINEAR)
                if not wmw2:
                    sprite_pos += [(sprite_size[0] / 2) - 1, (-sprite_size[1] / 2) - 7]
                else:
                    sprite_pos += [1, (-sprite_size[1] / 2) - 5]
            else:
                sprite_image = sprite.image
        else:
            sprite_image = sprite.image
        return sprite_image, sprite_pos

    def icicle_corner(sprite, filename, sprite_image, sprite_pos, sprite_size, glow_name, wmw2=False):
        if 'filename' in sprite.properties:
            filename = sprite.properties['filename']
            if glow_name in filename.lower():
                sprite_image = sprite.image.rotate(180, resample = Image.BILINEAR)
                if not wmw2:
                    sprite_pos += [(-sprite_size[0] / 2) + 1, (-sprite_size[1] / 2) - 7]
                else:
                    sprite_pos += [1, (-sprite_size[1] / 2) - 5]
            else:
                sprite_image = sprite.image
        else:
            sprite_image = sprite.image
        return sprite_image, sprite_pos

    def icicle_large(sprite, filename, sprite_image, sprite_pos, glow_name, wmw2=False):
        if 'filename' in sprite.properties:
            filename = sprite.properties['filename']
            if glow_name in filename.lower():
                if not wmw2:
                    sprite_image = sprite.image.rotate(180, resample = Image.BILINEAR)
                    sprite_pos += [0, -5.5]
                else:
                    sprite_pos += [0, -0.5]
            else:
                sprite_image = sprite.image
        else:
            sprite_image = sprite.image
        return sprite_image, sprite_pos

    def icicle_small(sprite, filename, sprite_image, sprite_pos, glow_name, wmw2=False):
        if 'filename' in sprite.properties:
            filename = sprite.properties['filename']
            if glow_name in filename.lower():
                if not wmw2:
                    sprite_image = sprite.image.rotate(180, resample = Image.BILINEAR)
                    sprite_pos += [0, -3.5]
                else:
                    sprite_pos += [0, -0.5]
            else:
                sprite_image = sprite.image
        else:
            sprite_image = sprite.image
        return sprite_image, sprite_pos

    def icicle_medium(sprite, filename, sprite_image, sprite_pos, glow_name, wmw2=False):
        if 'filename' in sprite.properties:
            filename = sprite.properties['filename']
            if glow_name in filename.lower():
                if not wmw2:
                    sprite_image = sprite.image.rotate(180, resample = Image.BILINEAR)
                    sprite_pos += [0, -4.5]
                else:
                    sprite_pos += [0, -0.5]
            else:
                sprite_image = sprite.image
        else:
            sprite_image = sprite.image
        return sprite_image, sprite_pos