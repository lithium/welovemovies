import cachemodel
import pytz
import twitter
from allauth.socialaccount.models import SocialApp, SocialToken
from django.contrib.auth.models import Group, AbstractUser, UserManager
from django.contrib.sites.models import Site
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse
from django.db import models

from challenge.models import ActiveChallenge
from mainsite.models import StatsMixin
from welovemovies.models import Viewing, Schedule


TZ_CHOICES = [(str(t), str(t)) for t in pytz.all_timezones]


class WlmUser(StatsMixin, cachemodel.CacheModel, AbstractUser):
    objects = UserManager()
    timezone = models.CharField(max_length=254, default='US/Pacific', choices=TZ_CHOICES)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def publish(self):
        super(WlmUser, self).publish()
        self.publish_by('username')

    def delete(self, *args, **kwargs):
        self.publish_delete('username')
        return super(WlmUser, self).delete()

    def get_absolute_url(self):
        return reverse('public_profile', kwargs={'username': self.username})

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

    def unwatched_movies(self):
        filtered = filter(lambda v: v.status == Viewing.STATUS_UNWATCHED, self.cached_viewings())
        scheduled = filter(lambda v: v.scheduled_for, filtered)
        unscheduled = sorted(filter(lambda v: not v.scheduled_for, filtered), lambda x,y: cmp(x.movie.title,y.movie.title))
        return scheduled + unscheduled

    def social_account(self, provider_id):
        return self.socialaccount_set.filter(provider=provider_id).first()

    @property
    def avatar_url(self):
        account = self.social_account('twitter')
        if account and 'profile_image_url' in account.extra_data:
            return account.extra_data.get('profile_image_url')
        return staticfiles_storage.url("images/avatar-placeholder.png")

    @property
    def unwatched_count(self):
        return len(self.unwatched_movies())

    def active_challenge(self, request):
        site = Site.objects.get_current(request)
        active = ActiveChallenge.cached.get(site=site)
        return active.challenge

    def viewing_graph(self, request=None, challenge=None):
        if challenge is None:
            challenge = self.active_challenge(request=request)

        days = {}
        filtered_viewings = filter(lambda v: v.viewed_on >= challenge.start and v.viewed_on <= challenge.end, self.watched_movies())
        for viewing in filtered_viewings:
            item = days.get(viewing.viewed_on, {
                'viewings': []
            })
            item['viewings'].append(viewing)
            days[viewing.viewed_on] = item

        return days

    @property
    def has_twitter(self):
        return self.social_account('twitter') is not None

    def tweet(self, message):
        account = self.social_account('twitter')
        if not account:
            return

        try:
            app = SocialApp.objects.get(provider='twitter')
        except SocialApp.DoesNotExist:
            return

        try:
            token = SocialToken.objects.get(app=app, account=account)
        except SocialToken.DoesNotExist:
            return

        api = twitter.Api(consumer_key=app.client_id,
                          consumer_secret=app.secret,
                          access_token_key=token.token,
                          access_token_secret=token.token_secret)
        return api.PostUpdate(message)







class ProxyGroup(Group):
    class Meta:
        proxy = True
        app_label = 'wlmuser'
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'