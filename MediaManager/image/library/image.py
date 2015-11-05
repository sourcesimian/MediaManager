import os
import shutil


class ImageInfo(object):
    _image_exts = ('jpg', 'jpeg', 'png', 'gif')

    def __init__(self, file_path):
        self.__file_path = file_path

    @property
    def mime_type(self):
        return 'image/jpeg'

    @property
    def data(self):
        return open(self.__file_path, 'rb').read()

    @classmethod
    def is_valid_ext(cls, ext):
        if not ext:
            return False
        if ext[0] == '.':
            ext = ext[1:]
        ext = ext.lower()
        return ext in cls._image_exts

    def write_to(self, dest_dir):
        file_name = os.path.split(self.__file_path)[1]
        dest_path = os.path.join(dest_dir, file_name)
        shutil.copy(self.__file_path, dest_path)

