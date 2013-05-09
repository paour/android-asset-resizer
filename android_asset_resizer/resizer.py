import os
from PIL import Image


DENSITY_TYPES = ('ldpi', 'mdpi', 'hdpi', 'xhdpi', 'xxhdpi')
DENSITY_MAP = {
    'ldpi': float(3),
    'mdpi': float(4),
    'hdpi': float(6),
    'xhdpi': float(8),
    'xxhdpi': float(12),
}


class AssetResizer():
    def __init__(self, out, source_density='xhdpi', prefix='',
            image_filter=Image.ANTIALIAS):
        if source_density not in DENSITY_TYPES:
            raise ValueError('source_density must be one of %s' % str(DENSITY_TYPES))

        self.out = os.path.abspath(out)
        self.source_density = source_density
        self.prefix = prefix
        self.image_filter = image_filter

    def mkres(self):
        """
        Create a directory tree for the resized assets
        """
        for d in DENSITY_TYPES:
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

    def get_size_for_density(self, size, target_density):
        """
        Return the new image size for the target density
        """
        current_size = size
        current_density = DENSITY_MAP[self.source_density]
        target_density = DENSITY_MAP[target_density]

        return int(current_size * (target_density / current_density))

    def get_safe_filename(self, filename):
        """
        Return a sanitized image filename
        """
        return filename.replace('@2x', '').replace('-', '_')

    def resize(self, path):
        """
        Generate assets from the given image
        """
        im = Image.open(path)

        # Get the original filename
        _, filename = os.path.split(path)

        # Generate the new filename
        filename = self.get_safe_filename(filename)
        filename = '%s%s' % (self.prefix if self.prefix else '', filename)

        # Get the original image size
        w, h = im.size

        # Generate assets from the source image
        for d in DENSITY_TYPES:
            out_file = os.path.join(self.out,
                    self.get_out_for_density(d), filename)

            if d == self.source_density:
                im.save(out_file)
            else:
                size = (self.get_size_for_density(w, d),
                        self.get_size_for_density(h, d))
                im.resize(size, self.image_filter).save(out_file)