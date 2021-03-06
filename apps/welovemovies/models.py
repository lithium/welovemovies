from hashlib import md5

import cachemodel
import re

import datetime

import pytz
from django.conf import settings
from django.core.files.storage import DefaultStorage
from django.core.urlresolvers import reverse
from django.db import models
from imdb.utils import RolesList

from mainsite.models import DefaultModel, CachedSite
from welovemovies.helpers import ImdbHelper, TweetScraper


class MovieManager(models.Manager):

    def get_from_title_match(self, match):
        try:
            kwargs = {
                'title': match.get('title')
            }
            if match.get('year'):
                kwargs['year'] = match.get('year')
            movie = Movie.cached.get(**kwargs)
            return movie
        except Movie.DoesNotExist:
            pass

    def get_or_create_from_tweet(self, tweet):
        if tweet['text'].startswith('RT'):
            return None, False

        match = TweetScraper.search_for_title(tweet['text'])
        if match:
            movie = self.get_from_title_match(match)
            if movie:
                return movie, False

            results = TweetScraper.imdb_results_for_tweet(match)
            if results is not None and len(results) > 0:
                r = results[0]
                y = r.get('year')
                t = r.get('title')
                imdb_id = r.getID()
                movie, created = Movie.cached.get_or_create(imdb_id=imdb_id)
                if created:
                    movie.fetch_imdb(max_cast=0)
                return movie, created

        return None, False


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

    objects = MovieManager()

    def __unicode__(self):
        if self.year:
            return u"{} ({})".format(self.title, self.year)
        return self.title

    def publish(self):
        super(Movie, self).publish()
        self.publish_by('imdb_id')

    def delete(self, *args, **kwargs):
        self.publish_delete('imdb_id')
        for viewing in self.cached_viewings():
            viewing.delete()
        return super(Movie, self).delete(*args, **kwargs)

    def fetch_imdb(self, max_cast=None):
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
            self.save()

            for director in imdb_movie.get('director', []):
                meta, created = MovieMetadata.cached.get_or_create(movie=self, key='director', source='imdb', source_id=director.getID())
                if created:
                    meta.value = director.get('name')
                    meta.save()

            for genre in imdb_movie.get('genres', []):
                try:
                    meta, created = MovieMetadata.cached.get_or_create(movie=self, key='genre', source='imdb', value=genre)
                except UnicodeEncodeError:
                    pass

            i = 1
            for cast in imdb_movie.get('cast', []):
                if max_cast is not None and i >= max_cast:
                    break
                person, created = Person.cached.get_or_create(imdb_id=cast.getID())
                person.name = cast.get('name')
                person.save()

                movie_cast, created = MovieCast.cached.get_or_create(movie=self, person=person)
                role = getattr(cast, 'currentRole')
                if isinstance(role, RolesList):
                    movie_cast.role = u' / '.join(r.get('name') for r in role)
                elif role:
                    movie_cast.role = role.get('name')
                movie_cast.ordering = i
                movie_cast.save()
                i += 1

            return True

    @cachemodel.cached_method(auto_publish=True)
    def cached_viewings(self):
        return self.viewing_set.all()

    @cachemodel.cached_method(auto_publish=True)
    def cached_directors(self):
        return self.moviemetadata_set.filter(key='director')

    @cachemodel.cached_method(auto_publish=True)
    def cached_genres(self):
        return self.moviemetadata_set.filter(key='genre')

    @property
    def directors(self):
        return map(lambda m: m.value, self.cached_directors())

    @property
    def genres(self):
        return map(lambda m: m.value, self.cached_genres())

    @cachemodel.cached_method(auto_publish=True)
    def cached_cast(self):
        return self.moviecast_set.all()

    @property
    def cached_cover_url(self):
        if self.cover_url:
            digest = md5(self.cover_url).hexdigest()
            store = DefaultStorage()
            storage_name = "imdb/image/{}".format(digest)
            if store.exists(storage_name):
                return "{}{}".format(settings.MEDIA_URL, storage_name)
        return reverse('movie_cover', kwargs={'movieID': self.imdb_id})

    @property
    def cached_large_cover_url(self):
        if self.large_cover_url:
            digest = md5(self.large_cover_url).hexdigest()
            store = DefaultStorage()
            storage_name = "imdb/image/{}".format(digest)
            if store.exists(storage_name):
                return "{}{}".format(settings.MEDIA_URL, storage_name)
        return "{}?size=full".format(reverse('movie_cover', kwargs={'movieID': self.imdb_id}))

    @property
    def decade(self):
        if self.year:
            return self.year - (self.year % 10)

    def get_runtime_display(self):
        if self.runtime:
            hours = self.runtime / 60
            minutes = self.runtime % 60
            if hours > 0:
                return u"{hours}h {minutes}min".format(hours=hours, minutes=minutes)
            return u"{minutes}min".format(minutes=minutes)


class Person(DefaultModel):
    imdb_id = models.CharField(max_length=254, unique=True)
    name = models.CharField(max_length=254)

    def __unicode__(self):
        if self.name:
            return self.name
        return self.imdb_id

    def publish(self):
        super(Person, self).publish()
        self.publish_by('imdb_id')


class MovieCast(DefaultModel):
    movie = models.ForeignKey('welovemovies.Movie')
    person = models.ForeignKey('welovemovies.Person')
    role = models.CharField(max_length=254, blank=True, null=True)
    ordering = models.IntegerField(default=99)

    class Meta:
        ordering = ('ordering',)

    def __unicode__(self):
        if self.role:
            return u"{} as {}".format(self.person.name, self.role)
        return unicode(self.person)

    def publish(self):
        super(MovieCast, self).publish()
        self.publish_by('movie', 'person')
        self.person.publish()
        self.movie.publish()


class MovieMetadata(DefaultModel):
    movie = models.ForeignKey('welovemovies.Movie')
    source = models.CharField(max_length=254, blank=True, null=True)
    source_id = models.CharField(max_length=254, blank=True, null=True)
    key = models.CharField(max_length=254, db_index=True)
    value = models.TextField()

    def publish(self):
        super(MovieMetadata, self).publish()
        self.publish_by('movie', 'key', 'source', 'source_id')
        self.publish_by('movie', 'key', 'source', 'value')


class ViewingManager(models.Manager):

    def get_or_create_from_tweet(self, tweet):
        movie, movie_created = Movie.objects.get_or_create_from_tweet(tweet)

        if movie:
            from wlmuser.models import WlmUser
            user, created = WlmUser.cached.get_or_create(username=tweet['user']['screen_name'])
            if created:
                user.twitter_screen_name = tweet['user']['screen_name']
                user.twitter_profile_image_url = tweet['user']['profile_image_url']
                user.save()

            viewing, created = Viewing.objects.get_or_create(movie=movie, viewer=user)
            if created:
                viewing.status = Viewing.STATUS_WATCHED
                viewing.summary = tweet['text']
                created_at = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y').replace(tzinfo=pytz.utc)
                viewing.viewed_on = created_at
                viewing.twitter_status_id = tweet['id']
                viewing.save()
            return viewing, created
        return None, False


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
    summary = models.TextField(blank=True, null=True)
    how_watched = models.CharField(max_length=254, blank=True, null=True)
    twitter_status_id = models.CharField(max_length=254, blank=True, null=True)

    objects = ViewingManager()

    class Meta:
        ordering = ('scheduled_for',)

    def publish(self):
        super(Viewing, self).publish()
        self.publish_by('movie','viewer')
        self.movie.publish()
        self.viewer.publish()
        self.viewer.publish_method('favorite_directors')
        self.viewer.publish_method('favorite_genres')
        self.viewer.publish_method('favorite_decades')
        site = CachedSite.objects.get_current()
        site.publish()
        site.publish_method('favorite_directors')
        site.publish_method('favorite_genres')
        site.publish_method('favorite_decades')

    def delete(self, *args, **kwargs):
        self.publish_delete('movie','viewer')
        movie = self.movie
        viewer = self.viewer
        site = CachedSite.objects.get_current()
        ret = super(Viewing, self).delete(*args, **kwargs)
        movie.publish()
        viewer.publish()
        viewer.publish_method('favorite_directors')
        viewer.publish_method('favorite_genres')
        viewer.publish_method('favorite_decades')
        site.publish()
        site.publish_method('favorite_directors')
        site.publish_method('favorite_genres')
        site.publish_method('favorite_decades')
        return ret

    @property
    def visible_rating(self):
        if self.rating is None:
            return ""
        return self.get_rating_display()

    def __unicode__(self):
        return u"<Viewing viewer={} movie={}>".format(self.viewer, self.movie)


class ViewingCast(DefaultModel):
    viewing = models.ForeignKey('welovemovies.Viewing')
    actor = models.ForeignKey('welovemovies.MovieCast')


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

