import os

from MediaManager.audio.library.albumart import AlbumArtLibrary


class FakeAlbumInfo(object):
    artist = 'Bob Marley'
    title = 'One Love'

    @property
    def name(self):
        return '%s - %s' % (self.artist, self.title)

    def __str__(self):
        return self.name


def test_image_search_online(tmpdir):
    tmp_dir = tmpdir.strpath
    lib = AlbumArtLibrary(image_cache_path=tmpdir.mkdir("cache").strpath, online=True)

    album_info = FakeAlbumInfo()
    image_info = lib.cover_image(album_info)

    image_info.write_to(tmp_dir)

    assert 'cover.Bob Marley - One Love.jpg' in os.listdir(tmp_dir)
