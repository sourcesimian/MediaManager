import os
import sys


class AlbumInfo(object):
    _marker = '.album'

    def __init__(self, base_path):
        if base_path[-1] != os.path.sep:
            base_path += os.path.sep  # Ensure base path is '/' terminated for consistency
        self.__base_path = base_path

        self.__meta = None
        self.__file_map = None  # dict[path]: dict[ext]: [filename]
        self.__size = None

    @property
    def title(self):
        return self.__get_meta()['title']

    @property
    def artist(self):
        return self.__get_meta()['artist']

    @property
    def genre(self):
        return self.__get_meta().get('genre', None)

    @property
    def total_size(self):
        total_size = 0
        for disc_no, files_by_type in self.__get_disc_map().items():
            if 'audio' in files_by_type:
                for file_path in files_by_type['audio']:
                    total_size += os.path.getsize(self.__path(file_path))
        return total_size

    @property
    def disc_count(self):
        return len(self.__get_file_map())

    def track_count(self, for_disc_no=0):
        total = 0
        for disc_no, files_by_type in self.__get_disc_map().items():
            if 'audio' in files_by_type:
                if disc_no == for_disc_no or not for_disc_no:
                    total += len(files_by_type['audio'])
        return total

    @property
    def name(self):
        if not self.artist:
            name = '%s' % self.title
        else:
            name = '%s - %s' % (self.artist, self.title,)
        return name

    def itertracks(self):
        from MediaManager.audio.track import TrackInfo

        disk_map = self.__get_disc_map()
        for disc_no, files_by_type in disk_map.items():
            if disc_no == 0:
                continue
            for i, file_path in enumerate(files_by_type['audio']):
                track_no = i + 1
                try:
                    yield TrackInfo(self, disc_no, track_no, self.__path(file_path))
                except ValueError as e:
                    print('! Error loading TrackInfo: %s' % e.message, file=sys.stderr)

    def copy_to(self, dest_dir, adapt_track_info=lambda x: x):
        self.__write_marker_file(dest_dir)
        for track_info in self.itertracks():
            track_info = adapt_track_info(track_info)
            track_info.copy_to(dest_dir)

    def cover_image(self, disc_no):
        image_files = self.__images(disc_no)
        if image_files is None:
            return None

        from MediaManager.image.library.image import ImageInfo
        return ImageInfo(self.__path(self.__cover_image(image_files)))

    def __cover_image(self, image_files):
        for image in image_files:
            for pattern in ('front', 'cover'):
                if pattern in image.lower():
                    return image
        return image_files[0]

    def __images(self, disc_no):
        disc_map = self.__get_disc_map()

        try:
            image_files = disc_map[disc_no]['image']
        except KeyError:
            try:
                image_files = disc_map[0]['image']
            except KeyError:
                return None

        return image_files

    def write_cover_image(self, image_info, disc_no=0):
        disc_map = self.__get_disc_map()
        if disc_no == 0:
            dest_dir = self.__base_path
        else:
            dest_dir = os.path.split(disc_map[disc_no]['audio'][0])[0]

        image_info.write_to(dest_dir)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<AlbumInfo "%s">' % (self.__base_path,)

    def __lt__(self, other):
        if self.artist == other.artist:
            return self.title.lower() < other.title.lower()
        return self.artist.lower() < other.artist.lower()

    def __eq__(self, other):
        if self.artist == other.artist:
            return self.title.lower() == other.title.lower()
        return self.artist.lower() == other.artist.lower()

    def __path(self, path):
        return os.path.join(self.__base_path, path)

    def __get_meta(self):
        if self.__meta:
            return self.__meta
        marker = self.__read_marker_file()
        path = self.__analyse_path()
        path.update(marker)
        self.__meta = path
        return self.__meta

    def __read_marker_file(self):
        marker = {}
        marker_path = os.path.join(self.__base_path, self._marker)
        marker_file = open(marker_path, 'rt')
        for line in marker_file:
            line = line.split('#', 1)[0]
            line = line.rstrip()
            if not line:
                continue
            s = line.split('=', 2)
            key = s[0].rstrip()
            value = None
            if len(s) > 1:
                value = s[1].strip()
            marker[key] = value
        return marker

    def __write_marker_file(self, folder):
        with open(os.path.join(folder, self._marker), 'wt') as fh:
            def write(key, value):
                if value is None:
                    fh.write('%s = \n' % (key,))
                else:
                    fh.write('%s = %s\n' % (key, value))
            write('artist', self.artist)
            write('title', self.title)
            if self.genre:
                write('genre', self.genre)

    def __analyse_path(self):
        s = self.__base_path.split(os.sep)
        path = {}

        def decode(s):
            import codecs
            try:
                return bytes(s, 'utf-8').decode('utf-8') # py2: codecs.decode(s, 'UTF-8', 'replace')
            except UnicodeDecodeError:
                pass
            return codecs.decode(s, 'UTF-8', 'xmlcharsetreplace')

        try:
            path['artist'] = decode(s[-3])
            path['title'] = decode(s[-2])
        except UnicodeDecodeError as e:
            raise ValueError('%s: "%s"' % (e.message, repr(s[-3:-1])))

        artist = path['artist'].lower()
        title = path['title'].lower()

        if title.startswith(artist) and len(title) > len(artist):
            path['title'] = path['title'][len(path['artist']):].lstrip('-._ ')
        return path

    def __get_disc_map(self):
        file_map = self.__get_file_map()

        disc_map = {0: {}}
        disc_no = 1
        first_char_audio = set()
        for path in sorted(file_map.keys()):
            files_by_type = file_map[path]
            if not 'audio' in files_by_type:
                if not path:
                    disc_map[0] = files_by_type
            else:
                for type, files in files_by_type.items():
                    for file_name in files:

                        # Magic to advance disc number if track names are ALL prefixed with disc_no
                        if type == 'audio':
                            try:
                                first_char = int(file_name[0])
                                if first_char_audio == set([disc_no]) and first_char == (disc_no + 1):
                                    disc_no += 1
                                    first_char_audio = set()

                                first_char_audio.add(first_char)
                            except ValueError:
                                pass

                        file_path = os.path.join(path, file_name)

                        if disc_no not in disc_map:
                            disc_map[disc_no] = {}
                        if type not in disc_map[disc_no]:
                            disc_map[disc_no][type] = []
                        disc_map[disc_no][type].append(file_path)

                disc_no += 1
        return disc_map

    def __get_file_map(self):
        from MediaManager.audio.track import TrackInfo
        from MediaManager.image.library.image import ImageInfo

        if not self.__file_map:

            file_map = {}  # dict[path]: dict[file_type]: [file_name]
            for root, dirs, files in os.walk(self.__base_path, topdown=False):
                files_by_type = {}
                for file_name in files:
                    if file_name == self._marker:
                        continue

                    _, ext = os.path.splitext(file_name)

                    if TrackInfo.is_valid_ext(ext):
                        if 'audio' not in files_by_type:
                            files_by_type['audio'] = []
                        files_by_type['audio'].append(file_name)

                    elif ImageInfo.is_valid_ext(ext):
                        if 'image' not in files_by_type:
                            files_by_type['image'] = []
                        files_by_type['image'].append(file_name)

                    else:
                        if 'other' not in files_by_type:
                            files_by_type['other'] = []
                        files_by_type['other'].append(file_name)

                if files_by_type:
                    for k in files_by_type:
                        files_by_type[k] = sorted(files_by_type[k])
                    path = root[len(self.__base_path):]
                    file_map[path] = files_by_type
            self.__file_map = file_map

        return self.__file_map

    def __hash__(self):
        return hash(self.__str__())
