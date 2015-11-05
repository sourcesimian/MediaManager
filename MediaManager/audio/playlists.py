import os


class PlaylistLibrary(object):
    def __init__(self, base_path):
        self.__base_path = base_path

    def add_album(self, album_info):
        m3u_path = os.path.join(self.__base_path, '%s.m3u' % album_info.name)
        m3u_file = open(m3u_path, 'wt')
        m3u_file.write('# %s\n' % album_info.name)
        for track_info in album_info.itertracks():
            rel_path = self._rel_path(self.__base_path, track_info.path)
            m3u_file.write('%s\n' % rel_path)

    def _rel_path(self, path, file):
        common = os.path.commonprefix([path, file])
        common_parts = common.split(os.sep)[:-1]
        path_parts = self.__base_path.split(os.sep)[len(common_parts):]
        file_parts = file.split(os.sep)[len(common_parts):]
        rel = os.path.join(*((['..'] * len(path_parts)) + file_parts))
        return rel
