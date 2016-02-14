import cachemodel
from django.contrib.auth.models import Group, AbstractUser

from welovemovies.models import Viewing


class WlmUser(cachemodel.CacheModel, AbstractUser):

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    @cachemodel.cached_method(auto_publish=True)
    def cached_viewings(self):
        return self.viewing_set.all()

    def watched_movies(self):
        filtered =  filter(lambda v: v.status in (Viewing.STATUS_WATCHED, Viewing.STATUS_REWATCHED), self.cached_viewings())
        return filtered

    def unwatched_movies(self):
        return filter(lambda v: v.status == Viewing.STATUS_UNWATCHED, self.cached_viewings())




class ProxyGroup(Group):
    class Meta:
        proxy = True
        app_label = 'wlmuser'
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'