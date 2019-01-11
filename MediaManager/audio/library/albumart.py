import os
import sys
import re
import glob
import urllib.request, urllib.error, urllib.parse
import json


from MediaManager.image.library.image import ImageInfo

class AlbumArtLibrary(object):
    def __init__(self, image_cache_path, online=True):
        self.__image_cache_path = image_cache_path
        self.__not_found = {}
        self.__online = online

    def cover_image(self, album_info):
        if album_info in self.__not_found:
            return None

        file_name = 'cover.%s' % album_info.name
        glob_pattern = os.path.join(self.__image_cache_path, file_name + '*')
        glob_pattern = glob_pattern.replace('[', '?').replace(']', '?')
        files = glob.glob(glob_pattern)
        if files:
            return ImageInfo(files[0])

        print('# No match for: %s' % os.path.join(self.__image_cache_path, file_name + '*'))

        if not self.__online:
            self.__not_found[album_info] = None
            return None

        query = '"%s" %s album cover' % (album_info.artist, album_info.title)
        query = query.replace('_', ' ')
        query = query.replace('-', ' ')
        urls = self.__google_image_search(query)
        if not urls:
            self.__not_found[album_info] = None
            return None

        for url in urls:
            image_url = url['url']
            file_ext = url['ext']
            print('# Fetching: %s' % image_url)
            try:
                response = urllib.request.urlopen(image_url)
                break
            except (urllib.error.HTTPError, urllib.error.URLError) as e:
                print('! %s' % e, file=sys.stderr)
        else:
            self.__not_found[album_info] = None
            return None

        file_path = os.path.join(self.__image_cache_path, '%s.%s' % (file_name, file_ext))
        data = response.read()
        if not data:
            self.__not_found[album_info] = None
            return None

        open(file_path, 'wb').write(data)
        print('# Wrote: %s' % file_path)

        return ImageInfo(file_path)

    def __google_image_search(self, query):

        fields = {'tbm': 'isch',
                  'tbs': 'isz:m',
                  'q': query,
                  }

        url = ('https://www.google.com/search?' + urllib.parse.urlencode(fields))

        print('# Google Image Search: %s' % query)
        headers = {
            'Referer': '',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        }
        request = urllib.request.Request(url, None, headers)  #/* Enter the URL of your site here */})
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.URLError as e:
            print('! %s' % e, file=sys.stderr)
            return None

        content = response.read().decode()

        image_json = re.compile('<div class="rg_meta notranslate">(?P<image>.*?)</div>')
        images = []
        for m in image_json.finditer(content):
            try:
                images.append(json.loads(m.group('image')))
            except ValueError:
                pass

        return [{'url': i['ou'], 'ext': i['ity']} for i in images
                    if i['ity'] in ('jpg', 'jpeg', 'png', 'gif') and
                       i['oh'] >= 200 and
                       i['ow'] >= 200]
