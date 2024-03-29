import math
import re


from MediaManager.audio.track import TrackInfoAdapter


class TrackNameAdapter(TrackInfoAdapter):
    __padding = '-._ '

    def __init__(self, track_info):
        TrackInfoAdapter.__init__(self, track_info)

    def __str__(self):
        return '%s {%s}' % (self.title, self.file_name)

    @property
    def title(self):
        name = self._title()

        if self._base.album_info.track_title:
            class album:
                artist = self._base.album_info.artist
                title = self._base.album_info.title

            ctx = {
                'album': album,
                'title': name,
                'number': '-'.join([self._disc_no(), self._track_no()])
            }
            name = self._template(self._base.album_info.track_title, ctx)

        return name

    def _title(self):
        name = self._base.title

        name = self.__name_replace(name)
        name = self.__name_without_index(name)
        name = self.__name_without_prefix(name)
        name = self.__name_without_suffix(name)
        name = self.__name_cleanup_brackets(name)
        name = self.__name_without_string(name, self._base.album_info.artist)
        name = self.__name_without_string(name, self._base.album_info.title)

        return name

    def _template(self, template, ctx):

        def repl(matchobj):
            return str(eval(matchobj.group(0)[1:-1], ctx))      # pylint: disable=W0123
        return re.sub(r'{[0-9A-Za-z.-_\[\]\(\)\"\' ]+}', repl, template)

    def _disc_no(self):
        if self._base.album_info.disc_count > 1:
            order = int(math.log10(self._base.album_info.disc_count)) + 1
            format = '%%0%dd' % order
            disc = format % (self._base.disc_no,)
            return disc

    def _track_no(self):
        track_count = self._base.album_info.track_count(self._base.disc_no)
        order = int(math.log10(track_count)) + 1
        format = '%%0%dd' % order
        track = format % (self._base.track_no,)
        return track

    @property
    def file_name(self):
        track_no = self._track_no()
        number = '-'.join([self._disc_no(), track_no])

        title = ''
        if self._title() != track_no:
            title = ' %s' % (self._title(),)

        ext = '.%s' % (self._base.file_ext,)

        return ''.join([number, title, ext])

    def __name_without_index(self, name):
        # Has no real name
        m = re.match(r'[0-9 ]*(Track[ 0-9]+)', name, re.IGNORECASE)
        if m:
            return '%s' % (self._base.album_info.title)

        pattern = '[\(\[]?%d?-?0?%d[-\)\]]?(?P<tail>.*)' % (self._base.disc_no, self._base.track_no)
        track_no_re = re.compile(pattern)
        m = track_no_re.match(name)
        if m:
            name = ' '.join([v.strip(self.__padding) for v in [m.group(p) for p in ('tail',)]])

        pattern = ' %02d ' % (self._base.track_no,)
        name = self.__name_without_string(name, pattern)

        pattern = '(%02d)' % (self._base.track_no,)
        name = self.__name_without_string(name, pattern)

        pattern = ' %d%02d ' % (self._base.disc_no, self._base.track_no)
        name = self.__name_without_string(name, pattern)

        return name

    def __name_without_prefix(self, name):
        prefix = self._base.album_info.artist
        if name.startswith(prefix) and len(name) > len(prefix):
            name = name[len(prefix):].strip(self.__padding)

        prefix = self._base.album_info.title
        if name.startswith(prefix) and len(name) > len(prefix):
            name = name[len(prefix):].strip(self.__padding)

        prefix = '%s - %s' % (self._base.album_info.title, self._base.album_info.artist,)
        if name.startswith(prefix) and len(name) > len(prefix):
            name = name[len(prefix):].strip(self.__padding)

        return name.strip('-. ')

    def __name_without_suffix(self, name):
        title = self._base.album_info.title
        title = title.replace('[', '\[').replace(']', '\]')
        title = title.replace('(', '\(').replace(')', '\)')
        title = title.replace('.', '\.').replace('*', '\*').replace('?', '\?')
        m = re.match('(?P<head>.*)\[%s\]' % title, name, re.IGNORECASE)
        if m:
            name = m.group('head').strip(self.__padding)
        m = re.match('(?P<head>.*) Track [0-9]+', name, re.IGNORECASE)
        if m:
            name = m.group('head').strip(self.__padding)
        m = re.match('(?P<head>.*) Disc [0-9]+', name, re.IGNORECASE)
        if m:
            name = m.group('head').strip(self.__padding)
        return name

    def __name_cleanup_brackets(self, name):
        name = name.replace('( ', '(')
        name = name.replace(' )', ')')
        return name

    def __name_without_string(self, name, string):
        if string:
            parts = []
            for piece in name.split(string):
                parts.append(piece.strip(self.__padding))
            result = ' '.join(parts).strip(self.__padding)
            if result:
                return result
        return name

    def __name_replace(self, name):
        name = name.replace('_', ' ')
        return name
