import os
from MediaManager.audio.adapter.name import TrackNameAdapter
from MediaManager.audio.adapter.tag import TrackTagAdapter


class InfoLibrary(object):
    def __init__(self):
        pass

    def add_album(self, album_info, albumart_library=None):
        def adapt_track_info(track_info):
            track_info = TrackNameAdapter(track_info)
            track_info = TrackTagAdapter(track_info)
            return track_info

        print('* %s' % album_info.title)
        for t in album_info.itertracks():
            track_info = adapt_track_info(t)
            print('  %s | %s' % (track_info, os.path.split(t.file_name)[1]))

    def has_album_art(self, album_info):
        for disc_no in range(1, album_info.disc_count+1):
            if album_info.cover_image(disc_no):
                return True
        #print 'No album art for: "%s" %s album' % (album_info.artist, album_info.title)
        return False

    @property
    def available_space(self):
        return 0

    @property
    def base_dir(self):
        return None

    def has_album(self, item):
        return False

    def __iter__(self):
        for i in []:
            yield i
