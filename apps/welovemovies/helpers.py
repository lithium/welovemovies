
from django.core.cache import cache

import imdb


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
        return full_movie

    def get_movie(self, movieID):
        movie = cache.get(self.cache_key(movieID))
        if not movie:
            movie = self.cache_movie(movieID)
        return movie

    def cache_key(self, id, type='movie'):
        return 'imdb_{}_{}'.format(type, id)