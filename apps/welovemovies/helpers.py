import re
from hashlib import md5

import imdb
import requests
from django.core.cache import cache
from django.core.files.storage import DefaultStorage


class ImdbHelper(object):
    def __init__(self, **kwargs):
        self.imdb = imdb.IMDb(**kwargs)

    def search_movie(self, query, max_results=8, full_detail=True):
        results = self.imdb.search_movie(query, results=max_results)
        filtered_results = filter(lambda r: r.get('kind') == 'movie', results)
        if full_detail:
            full_results = map(lambda r: self.get_movie(r.getID()), filtered_results)
            return full_results
        return filtered_results

    def cache_movie(self, movieID):
        full_movie = self.imdb.get_movie(movieID)
        cache.set(self.cache_key(movieID), full_movie)

        # cover_url = full_movie.get('cover url')
        # if cover_url:
        #     self.download_image(cover_url)
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
        if not store.exists(storage_name):
            r = requests.get(image_url, stream=True)
            if r.status_code == 200:
                r.raw.decode_content = True
                store.save(storage_name, r.raw)
                return storage_name


class TweetScraper(object):
    _hashtags_strip = [
        re.compile(r'#dlmchallenge', re.IGNORECASE),
        re.compile(r'#366movies ?in ?#?366days', re.IGNORECASE),
        re.compile(r'#366movies', re.IGNORECASE),
        re.compile(r'#366days', re.IGNORECASE),
        re.compile(r'https?://[^ ]+', re.IGNORECASE),
    ]
    _title_res = [
        re.compile(r'(#|no\.?)?(?P<number>\d+)[ -:;.,]\s*(?P<title>[^-:;.,(\n]+)[-:;. \n]?\s*(\((?P<year>\d+)\))?(?P<summary>.*)', re.IGNORECASE)
    ]

    @classmethod
    def search_for_title(cls, message):
        msg = message
        for ht in TweetScraper._hashtags_strip:
            msg = ht.sub('', msg)

        for r in TweetScraper._title_res:
            match = r.search(msg)
            if match:
                d = match.groupdict()
                d['title'] = d['title'].replace('"','').strip()
                d['summary'] = d['summary'].strip()
                return d


    @classmethod
    def imdb_results_for_tweet(cls, tweet):
        match = TweetScraper.search_for_title(tweet.text)
        if match:
            imdb = ImdbHelper()
            results = imdb.search_movie(match.get('title'))

            def _match_result(r):
                title_matches = match.get('title').lower() == r.get('title').lower()
                if not title_matches:
                    return False
                if match.get('year'):
                    if not r.get('year') or int(match.get('year')) != int(r.get('year')):
                        return False
                return True

            match_title = filter(_match_result, results)
            match_sorted = sorted(match_title, cmp=lambda x, y: cmp(x.get('year'), y.get('year')), reverse=True)
            return match_sorted


