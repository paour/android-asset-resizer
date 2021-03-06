import os
import re
from PIL import Image

AUTO_DENSITY = 'auto'
DENSITY_TYPES = ('ldpi', 'mdpi', 'hdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi')
DENSITY_MAP = {
    'ldpi': float(3),
    'mdpi': float(4),
    'hdpi': float(6),
    'xhdpi': float(8),
    'xxhdpi': float(12),
    'xxxhdpi': float(16),
}


# noinspection PyIncorrectDocstring
class AssetResizer:
    def __init__(self, out, source_density='xhdpi', prefix='', ldpi=False,
                 xxxhdpi=False, image_filter=Image.ANTIALIAS, image_quality=None,
                 uprint=None,
                 premult=False):
        if source_density not in DENSITY_TYPES:
            raise ValueError('source_density must be one of %s' % str(DENSITY_TYPES))

        self.out = os.path.abspath(out)
        self.source_density = source_density
        self.prefix = prefix
        self.ldpi = ldpi
        self.xxxhdpi = xxxhdpi
        self.image_filter = image_filter
        self.image_quality = image_quality
        self.premult = premult
        self.uprint = uprint

    def mkres(self):
        """
        Create a directory tree for the resized assets
        """
        for d in DENSITY_TYPES:
            if d == 'ldpi' and not self.ldpi:
                continue  # skip ldpi
            if d == 'xxxhdpi' and not self.xxxhdpi:
                continue  # skip xxxhdpi

            try:
                path = os.path.join(self.out, 'res/drawable-%s' % d)
                os.makedirs(path, 0755)
            except OSError:
                pass

    def get_out_for_density(self, target_density):
        """
        Return the out directory for the given target density
        """
        return os.path.join(self.out, 'res/drawable-%s' % target_density)

    def get_size_for_density(self, size, source_density, target_density):
        """
        Return the new image size for the target density
        """
        current_size = size
        current_density = DENSITY_MAP[source_density]
        target_density = DENSITY_MAP[target_density]

        return int(current_size * (target_density / current_density))

    @staticmethod
    def get_safe_filename(filename):
        """
        Return a sanitized image filename
        """
        return re.sub("@[0-9]+x", "", filename).replace('-', '_')

    def resize(self, path):
        """
        Generate assets from the given image
        """
        return self.resize_image(path, Image.open(path))

    def determine_density(self, path):
        """
        Determine the probable density for the file
        """
        for d in DENSITY_TYPES:
            if path == 'res/drawable-%s' % d:
                return d

        raise ValueError("Couldn't resolve the density")

    def resize_image(self, path, im):
        """
        Generate assets from the given image and path in case you've already
        called Image.open
        """
        # Get the original filename
        parent, filename = os.path.split(path)

        # Generate the new filename
        filename = self.get_safe_filename(filename)
        filename = '%s%s' % (self.prefix if self.prefix else '', filename)

        # Get the original image size
        w, h = im.size

        if self.premult:
            im_premultiplied = im.copy()
            premultiply(im_premultiplied)
        else:
            im_premultiplied = im

        if self.source_density == AUTO_DENSITY:
            actual_source_density = self.determine_density(parent)
        else:
            actual_source_density = self.source_density

        # Generate assets from the source image
        for d in DENSITY_TYPES:
            if d == 'ldpi' and not self.ldpi:
                continue  # skip ldpi
            if d == 'xxxhdpi' and not self.xxxhdpi:
                continue  # skip xxxhdpi

            out_file = os.path.join(self.out,
                                    self.get_out_for_density(d), filename)

            if d == actual_source_density:
                im.save(out_file, quality=self.image_quality)

                if self.uprint:
                    self.uprint("Saved same size to %s" % out_file)
            else:
                size = (self.get_size_for_density(w, actual_source_density, d),
                        self.get_size_for_density(h, actual_source_density, d))

                im_resized = im_premultiplied.resize(size, self.image_filter)

                if self.premult:
                    unmultiply(im_resized)

                im_resized.save(out_file, quality=self.image_quality)

                if self.uprint:
                    self.uprint("Resized as %s to %s" % (d, out_file))

def premultiply(im):
    pixels = im.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, g, b, a = pixels[x, y]
            if a != 255:
                r = r * a // 255
                g = g * a // 255
                b = b * a // 255
                pixels[x, y] = (r, g, b, a)

def unmultiply(im):
    pixels = im.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, g, b, a = pixels[x, y]
            if a != 255 and a != 0:
                r = 255 if r >= a else 255 * r // a
                g = 255 if g >= a else 255 * g // a
                b = 255 if b >= a else 255 * b // a
                pixels[x, y] = (r, g, b, a)
