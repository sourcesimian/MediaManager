import os
import shutil


class TrackInfo(object):
    _audio_exts = ('mp3', 'mpc', 'wma', 'wav')

    def __init__(self, album_info, disc_no, track_no, file_path):
        self.__album_info = album_info
        self.__disc_no = int(disc_no)
        self.__track_no = int(track_no)

        def decode(s):
            import codecs
            try:
                return bytes(s, 'utf-8').decode('utf-8')  #py2: codecs.decode(s, 'UTF-8', 'replace')
            except UnicodeDecodeError:
                pass
            return codecs.decode(s, 'UTF-8', 'xmlcharsetreplace')

        try:
            self.__file_path = decode(file_path)
        except UnicodeDecodeError as e:
            raise ValueError('%s: "%s"' % (e.message, repr(file_path)))
        self.__genre = None

    @property
    def path(self):
        return self.__file_path

    @property
    def format(self):
        return os.path.splitext(self.__file_path)[1][1:].lower()

    @property
    def title(self):
        return self.file_name.strip()

    @property
    def file_name(self):
        return os.path.splitext(os.path.split(self.__file_path)[1])[0]

    @property
    def file_ext(self):
        return os.path.splitext(self.__file_path)[1].lower()[1:]

    @property
    def disc_no(self):
        return self.__disc_no

    @property
    def track_no(self):
        return self.__track_no

    @property
    def album_info(self):
        return self.__album_info

    @property
    def genre(self):
        if self.__genre:
            return self.__genre
        return self.__album_info.genre

    def __str__(self):
        return '%s {%s}' % (self.title, self.file_name)

    def __repr__(self):
        return self.__file_path

    def copy_to(self, dest_dir):
        dest_path = os.path.join(dest_dir, self.title)
        shutil.copyfile(self.__t.path, dest_path)

    @classmethod
    def is_valid_ext(cls, ext):
        if not ext:
            return False
        if ext[0] == '.':
            ext = ext[1:]
        ext = ext.lower()
        return ext in cls._audio_exts


class TrackInfoAdapter(object):
    def __init__(self, track_info):
        self._base = track_info

    @property
    def path(self):
        return self._base.path

    @property
    def format(self):
        return self._base.format

    @property
    def title(self):
        return self._base.title

    @property
    def file_name(self):
        return self._base.file_name

    @property
    def file_ext(self):
        return self._base.ext

    @property
    def disc_no(self):
        return self._base.disc_no

    @property
    def track_no(self):
        return self._base.track_no

    @property
    def album_info(self):
        return self._base.album_info

    @property
    def genre(self):
        return self._base.genre

    def __str__(self):
        return self._base.__str__()

    def __repr__(self):
        return self._base.__repr__()

    def copy_to(self, dest_dir):
        self._base.copy_to(dest_dir)