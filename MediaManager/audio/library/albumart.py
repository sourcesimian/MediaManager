import os
import sys
import glob
import urllib.request, urllib.error, urllib.parse
import json
import urllib.request, urllib.parse, urllib.error


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
        file_path = os.path.join(self.__image_cache_path, file_name + '*')
        files = glob.glob(file_path)
        if files:
            return ImageInfo(files[0])

        if not self.__online:
            self.__not_found[album_info] = None
            return None

        query = '"%s" %s album' % (album_info.artist, album_info.title)
        urls = self.__google_image_search(query)
        if not urls:
            self.__not_found[album_info] = None
            return None

        image_url = urls[0]
        file_ext = os.path.splitext(image_url)[1]

        print('Fetching: %s' % image_url)
        try:
            response = urllib.request.urlopen(image_url)
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            print('! %s' % (e), file=sys.stderr)
            self.__not_found[album_info] = None
            return None

        file_path = os.path.join(self.__image_cache_path, file_name + file_ext)
        data = response.read()
        if not data:
            self.__not_found[album_info] = None
            return None

        open(file_path, 'wb').write(data)

        return ImageInfo(file_path)

    def __google_image_search(self, query):
        query = query.replace('_', ' ')
        query = query.replace('-', ' ')

        fields = {'v': '1.0', 'q': query}

        url = ('https://ajax.googleapis.com/ajax/services/search/images?' + urllib.parse.urlencode(fields))
               # 'q=%s' % (query,)
               # 'v=1.0&q=barack%20obama&userip=INSERT-USER-IP')

        print('Google Image Search: %s' % query)
        request = urllib.request.Request(url, None, {'Referer': ''})  #/* Enter the URL of your site here */})
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.URLError as e:
            print(e, file=sys.stderr)
            return None

        # Process the JSON string.
        results = json.load(response)

        return [r['url'] for r in results['responseData']['results']]

