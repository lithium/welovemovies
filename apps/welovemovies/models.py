import imdb
from django.db import models

from mainsite.models import DefaultModel


class Movie(DefaultModel):
    # identifying information
    title = models.CharField(max_length=254)
    year = models.IntegerField(blank=True, null=True)
    runtime = models.IntegerField(blank=True, null=True)  # in minutes

    # imdb
    imdb_id = models.CharField(max_length=254, blank=True, null=True)
    imdb_plot_outline = models.CharField(max_length=254, blank=True, null=True)
    imdb_rating = models.CharField(max_length=254, blank=True, null=True)
    imdb_votes = models.CharField(max_length=254, blank=True, null=True)
    cover_url = models.URLField(blank=True, null=True)
    large_cover_url = models.URLField(blank=True, null=True)

    # rottentomatoes
    # rt_id = models.CharField(max_length=254, blank=True, null=True)
    # rt_consensus = models.CharField(max_length=254, blank=True, null=True)
    # rt_tomatoes = models.CharField(max_length=254, blank=True, null=True)

    def __unicode__(self):
        if self.year:
            return u"{} ({})".format(self.title, self.year)
        return self.title

    def fetch_imdb(self, imdb_access=None):
        if not self.imdb_id:
            return False
        if imdb_access is None:
            imdb_access = imdb.IMDb()
        try:
            imdb_movie = imdb_access.get_movie(self.imdb_id)
            if len(imdb_movie) == 0:
                return False
        except imdb.IMDbParserError:
            return False
        else:
            if not self.title:
                self.title = imdb_movie.get('title')
            if not self.year:
                self.year = imdb_movie.get('year')
            if not self.runtime:
                times = imdb_movie.get('runtimes')
                if times is not None and len(times) > 0:
                    try:
                        self.runtime = int(times[0])
                    except ValueError:
                        pass

            self.imdb_plot_outline = imdb_movie.get('plot outline')
            self.imdb_rating = imdb_movie.get('rating')
            self.imdb_votes = imdb_movie.get('votes')
            self.cover_url = imdb_movie.get('cover url')
            self.large_cover_url = imdb_movie.get('full-size cover url')
            self.save()
            return True


class MovieDescription(DefaultModel):
    movie = models.ForeignKey('welovemovies.Movie')
    description = models.TextField()


class MovieMetadata(DefaultModel):
    movie = models.ForeignKey('welovemovies.Movie')
    source = models.CharField(max_length=254, blank=True, null=True)
    key = models.CharField(max_length=254, db_index=True)
    value = models.TextField()


