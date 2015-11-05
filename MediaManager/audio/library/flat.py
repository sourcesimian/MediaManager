import shutil
import os

from MediaManager.audio.adapter.name import TrackNameAdapter
from MediaManager.audio.adapter.tag import TrackTagAdapter
from MediaManager.audio.album import AlbumInfo
from MediaManager.util.fs import available_space


class FlatLibrary(object):
    def __init__(self, base_dir):
        self.__base_dir = base_dir
        self.__catalog = {}
        self.__load_catalog()

    def __load_catalog(self):
        for folder in os.listdir(self.__base_dir):
            path = os.path.join(self.__base_dir, folder)
            if os.path.isfile(os.path.join(path, AlbumInfo._marker)):
                self.__catalog[folder] = AlbumInfo(path)

    def delete_album(self, name):
        if name not in self.__catalog:
            return
        album_dir = os.path.join(self.__base_dir, name)
        #print 'Removing "%s"' % (name,)
        shutil.rmtree(album_dir)
        del self.__catalog[name]

    def add_album(self, album_info, albumart_library=None):
        if album_info.name in self.__catalog:
            raise KeyError('Album "%s" already exist in FlatLibrary' % (album_info.name,))
        dest_dir = os.path.join(self.__base_dir, album_info.name)
        os.makedirs(dest_dir)

        def adapt_track_info(track_info):
            track_info = TrackNameAdapter(track_info)
            track_info = TrackTagAdapter(track_info, albumart_library)
            return track_info

        #print 'Adding "%s"' % (album_info.name,)
        album_info.copy_to(dest_dir, adapt_track_info)

    # def iterkeys(self):
    #     return self.__catalog.__iter__()

    def get_album(self, name):
        return self.__catalog[name]

    def has_album(self, item):
        if isinstance(item, AlbumInfo):
            item = item.name
        return item in self.__catalog

    @property
    def available_space(self):
        return available_space(self.__base_dir)

    @property
    def base_dir(self):
        return self.__base_dir

    def __iter__(self):
        for name in self.__catalog:
            yield self.__catalog[name]

    # def __contains__(self, item):
    #     if isinstance(item, AlbumInfo):
    #         item = item.name
    #     return item in self.__catalog
