import cachemodel
from django.contrib.sites.models import Site, SiteManager
from django.db import models
from django.conf import settings
from django.utils import timezone


class ActiveModelManager(cachemodel.CacheModelManager):
    def get_queryset(self):
        qs = super(ActiveModelManager, self).get_queryset()
        return qs.filter(is_active=True)


class DefaultModel(cachemodel.CacheModel):
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_created', null=True, blank=True, on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_updated', null=True, blank=True, on_delete=models.SET_NULL)

    objects = models.Manager()
    active_objects = ActiveModelManager()

    class Meta:
        abstract = True


class StatsMixin(object):
    def watched_movies(self):
        raise NotImplementedError

    @property
    def watched_count(self):
        return len(self.watched_movies())

    @property
    def recently_watched(self, count=3):
        sort = sorted(self.watched_movies(), lambda a,b: cmp(a.viewed_on, b.viewed_on), reverse=True)
        return sort[:count]

    @property
    def velocity(self):
        if self.watched_count < 1:
            return 0
        sort = sorted(self.watched_movies(), lambda a,b: cmp(a.viewed_on, b.viewed_on))
        first_movie = sort[0]
        timedelta = timezone.now().date() - first_movie.viewed_on
        num_days = float(timedelta.days)
        velocity = (float(self.watched_count) / num_days) if num_days > 0 else 0
        return velocity

    @cachemodel.cached_method(auto_publish=False)
    def favorite_directors(self):
        return self._favorite_movie_property('directors')

    @property
    def favorite_director(self):
        d = self.favorite_directors()
        if len(d) > 0:
            return d[0]

    @cachemodel.cached_method(auto_publish=False)
    def favorite_genres(self):
        return self._favorite_movie_property('genres')

    @property
    def favorite_genre(self):
        g = self.favorite_genres()
        if len(g) > 0:
            return g[0]

    @cachemodel.cached_method(auto_publish=False)
    def favorite_years(self):
        return self._favorite_movie_property('year')

    @property
    def favorite_year(self):
        g = self.favorite_years()
        if len(g) > 0:
            return g[0]

    @cachemodel.cached_method(auto_publish=False)
    def favorite_decades(self):
        return self._favorite_movie_property('decade')

    @property
    def favorite_decade(self):
        g = self.favorite_decades()
        if len(g) > 0:
            return g[0]

    def _favorite_movie_property(self, prop_name):
        index = {}
        for v in self.watched_movies():
            val = getattr(v.movie, prop_name)
            try:
                val_iter = iter(val)
                for p in val_iter:
                    index[p] = index.get(p, 0)+1
            except TypeError:
                index[val] = index.get(val, 0)+1

        sorted_items = sorted(index.items(), lambda x,y: cmp(y[1], x[1]))
        return sorted_items


class CachedSiteManager(SiteManager):
    def get_current(self, request=None):
        site = super(CachedSiteManager, self).get_current(request=request)
        return CachedSite.cached.get(pk=site.pk)


class CachedSite(StatsMixin, cachemodel.CacheModel, Site):

    objects = CachedSiteManager()

    class Meta:
        proxy = True

    @cachemodel.cached_method(auto_publish=True)
    def watched_movies(self):
        from challenge.models import ActiveChallenge
        from welovemovies.models import Viewing
        active = ActiveChallenge.cached.get(site=self)
        viewings = Viewing.objects.filter(status__in=(Viewing.STATUS_WATCHED, Viewing.STATUS_REWATCHED),
                                          viewed_on__gte=active.challenge.start,
                                          viewed_on__lte=active.challenge.end)
        return viewings

    def viewing_graph(self):
        days = {}
        for viewing in self.watched_movies():
            item = days.get(viewing.viewed_on, {
                'viewings': []
            })
            item['viewings'].append(viewing)
            days[viewing.viewed_on] = item
        return days
