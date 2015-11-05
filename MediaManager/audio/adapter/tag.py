import os
import sys
import shutil

from mutagen.mp3 import MP3, HeaderNotFoundError
from mutagen import id3
from MediaManager.audio.track import TrackInfoAdapter


class TrackTagAdapter(TrackInfoAdapter):
    # ref: http://en.wikipedia.org/wiki/ID3
    _id3_tags = {
        'AENC': 'Audio encryption',
        'APIC': 'Attached picture',
        'COMM': 'Comments',
        'COMR': 'Commercial frame',
        'ENCR': 'Encryption method registration',
        'EQUA': 'Equalization',  # replaced by EQU2 in v2.4
        'EQU2': 'Equalization',
        'ETCO': 'Event timing codes',
        'GEOB': 'General encapsulated object',
        'GRID': 'Group identification registration',
        'IPLS': 'Involved people list',  # replaced by TMCL and TIPL in v2.4
        'TMCL': 'Involved people list',
        'TIPL': 'Involved people list',
        'LINK': 'Linked information',
        'MCDI': 'Music CD identifier',
        'MLLT': 'MPEG location lookup table',
        'OWNE': 'Ownership frame',
        'PRIV': 'Private frame',
        'PCNT': 'Play counter',
        'POPM': 'Popularimeter',
        'POSS': 'Position synchronisation frame',
        'RBUF': 'Recommended buffer size',
        'RVAD': 'Relative volume adjustment',  # replaced by RVA2 in v2.4
        'RVA2': 'Relative volume adjustment',
        'RVRB': 'Reverb',
        'SYLT': 'Synchronized lyric/text',
        'SYTC': 'Synchronized tempo codes',
        'TALB': 'Album/Movie/Show title',
        'TBPM': 'Beats per minute (BPM)',
        'TCOM': 'Composer',
        'TCON': 'Content type',
        'TCOP': 'Copyright message',
        'TDAT': 'Date',  # 'replaced by TDRC in v2.4',
        'TDRC': 'Date',
        'TDLY': 'Playlist delay',
        'TENC': 'Encoded by',
        'TEXT': 'Lyricist/Text writer',
        'TFLT': 'File type',
        'TIME': 'Time',  # replaced by TDRC in v2.4
        'TIT1': 'Content group description',
        'TIT2': 'Title/songname/content description',
        'TIT3': 'Subtitle/Description refinement',
        'TKEY': 'Initial key',
        'TLAN': 'Language(s)',
        'TLEN': 'Length',
        'TMED': 'Media type',
        'TOAL': 'Original album/movie/show title',
        'TOFN': 'Original filename',
        'TOLY': 'Original lyricist(s)/text writer(s)',
        'TOPE': 'Original artist(s)/performer(s)',
        'TORY': 'Original release year',  # replaced by TDOR in v2.4
        'TDOR': 'Original release year',
        'TOWN': 'File owner/licensee',
        'TPE1': 'Lead performer(s)/Soloist(s)',
        'TPE2': 'Band/orchestra/accompaniment',
        'TPE3': 'Conductor/performer refinement',
        'TPE4': 'Interpreted, remixed, or otherwise modified by',
        'TPOS': 'Part of a set',
        'TPUB': 'Publisher',
        'TRCK': 'Track number/Position in set',
        'TRDA': 'Recording dates',  # replaced by TDRC in v2.4
        'TRSN': 'Internet radio station name',
        'TRSO': 'Internet radio station owner',
        'TSIZ': 'Size',  # deprecated in v2.4
        'TSRC': 'International Standard Recording Code (ISRC)',
        'TSSE': 'Software/Hardware and settings used for encoding',
        'TYER': 'Year',  # replaced by TDRC in v2.4
        'TXXX': 'User defined text information frame',
        'UFID': 'Unique file identifier',
        'USER': 'Terms of use',
        'USLT': 'Unsynchronized lyric/text transcription',
        'WCOM': 'Commercial information',
        'WCOP': 'Copyright/Legal information',
        'WOAF': 'Official audio file webpage',
        'WOAR': 'Official artist/performer webpage',
        'WOAS': 'Official audio source webpage',
        'WORS': 'Official internet radio station homepage',
        'WPAY': 'Payment',
        'WPUB': 'Publishers official webpage',
        'WXXX': 'User defined URL link frame',
    }
    __allowed_tags = (
        'APIC:',  # Piture
        'MCDI',  # Music CD identifier
        'TALB',  # Album/Movie/Show title
        'TCOM',  # Composer
        'TCON',  # Content type
        'TDRC',  # Date
        'TIT2',  # Title/songname/content description
        'TLEN',  # Length
        'TOAL',  # Original album/movie/show title
        'TPE1',  # Lead performer(s)/Soloist(s)
        'TPE2',  # Band/orchestra/accompaniment
        'TPUB',  # Publisher
        'TRCK',  # Track number/Position in set
        'WOAS',  # Official audio source webpage
    )
    # iTunes
    #   TIT2 = Name
    #   TPE1 = Artist
    #   TPE2 = Album Artist
    #   TALB = Album
    #   TCOM = Composer
    #   TCON = Genre

    def __init__(self, track_info, online_library=None):
        TrackInfoAdapter.__init__(self, track_info)
        self.__online_library = online_library

    def copy_to(self, dest_dir):
        src_path = self._base.path
        dest_path = os.path.join(dest_dir, self.file_name)

        shutil.copyfile(src_path, dest_path)

        self.__sanitize_tags(dest_path)

    def __sanitize_tags(self, file_path):
        method_name = '_%s__sanitize_tags_%s' % (self.__class__.__name__, self._base.format)
        if not hasattr(self, method_name):
            return
        method = getattr(self, method_name)
        method(file_path)

    def __sanitize_tags_mp3(self, file_path):
        try:
            audio = MP3(file_path, ID3=id3.ID3)
        except HeaderNotFoundError:
            print >> sys.stderr, '! Invalid MP3: %s' % self._base.path
            return

        # Collect allowed tags and remove ID3 from track
        tags = {}
        for k in audio.keys():
            if k in self.__allowed_tags:
                tags[k] = audio[k]
        audio.delete()

        # print '>>>> %s | %s | [%d:%d] %s' % (self._base.album_info.artist,
        #                                      self._base.album_info.title,
        #                                      self.disc_no,
        #                                      self.track_no,
        #                                      self.title)

        # Force tags
        if self._base.album_info.artist:
            value = self._base.album_info.artist
        else:
            value = self._base.album_info.title
        tags['TPE1'] = id3.TPE1(3, value)
        tags['TPE2'] = id3.TPE2(3, value)
        tags['TALB'] = id3.TALB(3, self._base.album_info.title)

        # print repr(self._base.path)
        # tags['COMM'] = id3.COMM(3, '%s' % self._base.path)

        if 'TIT2' not in tags:
            try:
                tags['TIT2'] = id3.TIT2(3, self._base.title)
            except UnicodeDecodeError:
                print >> sys.stderr, '! Error decoding title: %s' % repr(self._base.title)
                raise

        if 'TRCK' not in tags:
            tags['TRCK'] = id3.TRCK(3, '%d' % (self._base.track_no))

        if 'TPOS' not in tags:
            tags['TPOS'] = id3.TPOS(3, '%d' % (self._base.disc_no))

        if 'TCON' not in tags and self._base.genre:
            tags['TCON'] = id3.TCON(3, self._base.genre)

        if 'APIC' not in tags:
            def image_sources():
                yield self._base.album_info.cover_image(self._base.disc_no)
                if self.__online_library:
                    yield self.__online_library.cover_image(self._base.album_info)

            for image in image_sources():
                if image:
                    tags['APIC'] = id3.APIC(3, image.mime_type, 3, 'Front cover', image.data)
                    break
            else:
                #print ' ! No album art for: %s' % self._base
                pass

        # for k in tags:
        #     print '    + :%s: %s' % (k, tags[k])

        if audio.tags is None:
            audio.add_tags()

        for k in tags:
            audio.tags.add(tags[k])

        audio.save()

