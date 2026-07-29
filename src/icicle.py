from PIL import Image

class Icicle:
    def icicle_corner_left(sprite, filename, sprite_image, sprite_pos, sprite_size):
        if 'filename' in sprite.properties:
            filename = sprite.properties['filename']
            if 'icicle_corner_glow' in filename.lower():
                sprite_image = sprite.image.rotate(180, resample = Image.BILINEAR)
                sprite_pos = sprite_pos + [(sprite_size[0] / 2) - 1, (-sprite_size[1] / 2) - 7]
            else:
                sprite_image = sprite.image
        else:
            sprite_image = sprite.image
        return sprite_image, sprite_pos

    def icicle_corner(sprite, filename, sprite_image, sprite_pos, sprite_size):
        if 'filename' in sprite.properties:
            filename = sprite.properties['filename']
            if 'icicle_corner_glow' in filename.lower():
                sprite_image = sprite.image.rotate(180, resample = Image.BILINEAR)
                sprite_pos = sprite_pos + [(-sprite_size[0] / 2) + 1, (-sprite_size[1] / 2) - 7]
            else:
                sprite_image = sprite.image
        else:
            sprite_image = sprite.image
        return sprite_image, sprite_pos