import os
import sys
import glob
import urllib2
import json
import urllib


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

        print 'Fetching: %s' % image_url
        try:
            response = urllib2.urlopen(image_url)
        except (urllib2.HTTPError, urllib2.URLError), e:
            print >> sys.stderr, '! %s' % (e)
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

        url = ('https://ajax.googleapis.com/ajax/services/search/images?' + urllib.urlencode(fields))
               # 'q=%s' % (query,)
               # 'v=1.0&q=barack%20obama&userip=INSERT-USER-IP')

        print 'Google Image Search: %s' % query
        request = urllib2.Request(url, None, {'Referer': ''})  #/* Enter the URL of your site here */})
        try:
            response = urllib2.urlopen(request)
        except urllib2.URLError, e:
            print >> sys.stderr, e
            return None

        # Process the JSON string.
        results = json.load(response)

        return [r['url'] for r in results['responseData']['results']]

