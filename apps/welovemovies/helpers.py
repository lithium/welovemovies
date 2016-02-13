import shutil
from hashlib import md5

import imdb
import requests
from django.core.cache import cache
from django.core.files.storage import DefaultStorage

class ImdbHelper(object):

    def __init__(self, **kwargs):
        self.imdb = imdb.IMDb(**kwargs)

    def search_movie(self, query, max_results=8):
        results = self.imdb.search_movie(query, results=max_results)
        filtered_results = filter(lambda r: r.get('kind') == 'movie', results)
        full_results = map(lambda r: self.get_movie(r.getID()), filtered_results)
        return full_results

    def cache_movie(self, movieID):
        full_movie = self.imdb.get_movie(movieID)
        cache.set(self.cache_key(movieID), full_movie)

        cover_url = full_movie.get('cover url')
        if cover_url:
            self.download_image(cover_url)
        return full_movie

    def get_movie(self, movieID):
        movie = cache.get(self.cache_key(movieID))
        if not movie:
            movie = self.cache_movie(movieID)
        return movie

    def cache_key(self, id, type='movie'):
        return 'imdb_{}_{}'.format(type, id)

    def download_image(self, image_url):
        store = DefaultStorage()
        storage_name = 'imdb/image/{}'.format(md5(image_url).hexdigest())
        # storage_name = store.get_available_name(storage_name)

        r = requests.get(image_url, stream=True)
        if r.status_code == 200:
            r.raw.decode_content = True
            store.save(storage_name, r.raw)
            # with store.open(storage_name, 'wb') as storage_fh:
            #     shutil.copyfileobj(r.raw, storage_fh)

