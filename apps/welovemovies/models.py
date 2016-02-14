from hashlib import md5

import cachemodel
from django.conf import settings
from django.db import models

from mainsite.models import DefaultModel
from welovemovies.helpers import ImdbHelper


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

    def publish(self):
        super(Movie, self).publish()
        self.publish_by('imdb_id')

    def delete(self, *args, **kwargs):
        self.publish_delete('imdb_id')
        return super(Movie, self).delete(*args, **kwargs)

    def fetch_imdb(self):
        if not self.imdb_id:
            return False
        imdb = ImdbHelper()
        imdb_movie = imdb.get_movie(self.imdb_id)
        if imdb_movie:
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
            if self.large_cover_url:
                imdb.download_image(self.large_cover_url)
            self.save()
            return True

    @cachemodel.cached_method(auto_publish=True)
    def cached_viewings(self):
        return self.viewing_set.all()

    @property
    def cached_cover_url(self):
        if self.cover_url:
            digest = md5(self.cover_url).hexdigest()
            return "{}imdb/image/{}".format(settings.MEDIA_URL, digest)
        else:
            return "{}images/cover-placeholder.png".format(settings.STATIC_URL)

    @property
    def cached_large_cover_url(self):
        if self.large_cover_url:
            digest = md5(self.large_cover_url).hexdigest()
            return "{}imdb/image/{}".format(settings.MEDIA_URL, digest)
        else:
            return "{}images/cover-placeholder.png".format(settings.STATIC_URL)


class MovieDescription(DefaultModel):
    movie = models.ForeignKey('welovemovies.Movie')
    description = models.TextField()


class MovieMetadata(DefaultModel):
    movie = models.ForeignKey('welovemovies.Movie')
    source = models.CharField(max_length=254, blank=True, null=True)
    key = models.CharField(max_length=254, db_index=True)
    value = models.TextField()


class Viewing(DefaultModel):
    STATUS_UNWATCHED = 'unwatched'
    STATUS_WATCHED = 'watched'
    STATUS_REWATCHED = 'rewatched'
    STATUS_CHOICES = (
        (STATUS_UNWATCHED, 'Un-watched'),
        (STATUS_WATCHED, 'Watched'),
        (STATUS_REWATCHED, 'Re-watched'),
    )

    RATING_LOVE = 'love'
    RATING_LIKE = 'like'
    RATING_HATE = 'hate'
    RATING_HATELIKE = 'hatelike'
    RATING_CHOICES = (
        (RATING_LOVE, 'Loved it'),
        (RATING_LIKE, 'Liked it'),
        (RATING_HATE, 'Hated it'),
        (RATING_HATELIKE, 'Hate myself for liking it'),
    )
    viewer = models.ForeignKey(settings.AUTH_USER_MODEL)
    movie = models.ForeignKey('welovemovies.Movie')
    status = models.CharField(max_length=254, choices=STATUS_CHOICES, default=STATUS_UNWATCHED)
    viewed_on = models.DateField(blank=True, null=True)
    scheduled_for = models.DateField(blank=True, null=True)
    rating = models.CharField(max_length=254, choices=RATING_CHOICES, blank=True, null=True)
    summary = models.CharField(max_length=254, blank=True, null=True)

    class Meta:
        ordering = ('scheduled_for',)

    def publish(self):
        super(Viewing, self).publish()
        self.movie.publish()
        self.viewer.publish()


class Schedule(cachemodel.CacheModel):
    FIELD_NAMES = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    challenge = models.ForeignKey('challenge.Challenge')
    monday = models.IntegerField(default=1)
    tuesday = models.IntegerField(default=1)
    wednesday = models.IntegerField(default=1)
    thursday = models.IntegerField(default=1)
    friday = models.IntegerField(default=1)
    saturday = models.IntegerField(default=1)
    sunday = models.IntegerField(default=1)

    class Meta:
        unique_together = ('challenge', 'owner')

    def publish(self):
        super(Schedule, self).publish()
        self.owner.publish()

    def get_day(self, weekday):
        """
        Return the value for the 0..6 weekday
        """
        return getattr(self, Schedule.FIELD_NAMES[weekday])

    def set_day(self, weekday, value):
        """
        Sets the schedule the 0..6 weekday
        """
        return setattr(self, Schedule.FIELD_NAMES[weekday], value)

    @property
    def total_per_week(self):
        return sum(self.get_day(i) for i in range(0,7))

    @property
    def avg_per_day(self):
        return self.total_per_week/7.0
