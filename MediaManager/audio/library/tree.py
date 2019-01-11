import os
import sys

from MediaManager.util.fs import available_space

class TreeLibrary(object):
    def __init__(self, base_path):
        self.__base_path = base_path
        self.__catalog = {}
        self.__load_catalog()

    def __load_catalog(self):
        from MediaManager.audio.album import AlbumInfo

        for root, dirs, files in os.walk(self.__base_path, topdown=False):
            if not AlbumInfo._marker in files:
                continue

            try:
                album = AlbumInfo(root)

                if album.track_count == 0:
                    print('Empty album: "%s"' % repr(album), file=sys.stderr)
                    continue

                if album.name in self.__catalog:
                    print('Ignoring duplicate album: "%s"' % (album.name,), file=sys.stderr)
                    print(' - "%s"' % repr(self.__catalog[album.name]), file=sys.stderr)
                    print(' - "%s"' % repr(album), file=sys.stderr)
                    continue

                self.__catalog[album.name] = album

            except ValueError as e:
                print('! %s: %s' % (e.message, root), file=sys.stderr)

    def get_album(self, name):
        return self.__catalog[name]

    # def iterkeys(self):
    #     return self.__catalog.iterkeys()
    #
    # def itervalues(self):
    #     return self.__catalog.itervalues()
    #
    def __iter__(self):
        for name in self.__catalog:
            yield self.__catalog[name]

    def has_album(self, item):
        return item in self.__catalog

    def available_space(self):
        return available_space(self.__base_dir)
