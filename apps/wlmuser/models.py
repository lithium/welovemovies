import cachemodel
from django.contrib.auth.models import Group, AbstractUser, UserManager
from django.contrib.sites.models import Site

from challenge.models import ActiveChallenge
from welovemovies.models import Viewing, Schedule


class WlmUser(cachemodel.CacheModel, AbstractUser):
    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    @cachemodel.cached_method(auto_publish=True)
    def cached_viewings(self):
        return self.viewing_set.all()

    @cachemodel.cached_method(auto_publish=True)
    def cached_schedules(self):
        return self.schedule_set.all()

    def cached_schedule(self, request):
        challenge = self.active_challenge(request)
        filtered = filter(lambda s: s.challenge_id == challenge.id, self.cached_schedules())
        if len(filtered) > 0:
            return filtered[0]
        schedule = Schedule(owner=self, challenge=challenge)
        schedule.save()
        return schedule

    def watched_movies(self):
        filtered = filter(lambda v: v.status in (Viewing.STATUS_WATCHED, Viewing.STATUS_REWATCHED), self.cached_viewings())
        return filtered

    @property
    def watched_count(self):
        return len(self.watched_movies())

    def unwatched_movies(self):
        return filter(lambda v: v.status == Viewing.STATUS_UNWATCHED, self.cached_viewings())

    @property
    def unwatched_count(self):
        return len(self.unwatched_movies())

    def active_challenge(self, request):
        site = Site.objects.get_current(request)
        active = ActiveChallenge.cached.get(site=site)
        return active.challenge

    @cachemodel.cached_method(auto_publish=False)
    def favorite_directors(self):
        return self._favorite_movie_property('directors')

    @property
    def favorite_director(self):
        d = self.favorite_directors()
        if len(d) > 0:
            return d[0]

    @property
    def favorite_genre(self):
        g = self.favorite_genres()
        if len(g) > 0:
            return g[0]

    @cachemodel.cached_method(auto_publish=False)
    def favorite_genres(self):
        return self._favorite_movie_property('genres')

    def _favorite_movie_property(self, prop_name):
        index = {}
        for v in self.cached_viewings():
            for p in getattr(v.movie, prop_name):
                index[p] = index.get(p, 0)+1
        sorted_items = sorted(index.items(), lambda x,y: cmp(y[1], x[1]))
        # ret = map(lambda l: {prop_name: l[0], 'count': l[1]}, sorted_genres)
        return sorted_items





class ProxyGroup(Group):
    class Meta:
        proxy = True
        app_label = 'wlmuser'
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'