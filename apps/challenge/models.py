import datetime
from django.utils import timezone

from mainsite.models import DefaultModel
from django.db import models


class Challenge(DefaultModel):
    name = models.CharField(max_length=254)
    description = models.CharField(max_length=254, blank=True, null=True)
    start = models.DateField()
    end = models.DateField()
    how_many_movies = models.IntegerField()

    def __unicode__(self):
        return self.name

    @property
    def how_many_days(self):
        return (self.end - self.start).days+1

    @property
    def days_left(self, whence=None):
        if whence is None:
            whence = timezone.now().date()
        return (self.end - whence).days+1

    @property
    def day_number(self, whence=None):
        if whence is None:
            whence = timezone.now().date()
        return (whence - self.start).days+1


class ActiveChallenge(DefaultModel):
    challenge = models.ForeignKey('challenge.Challenge')
    site = models.ForeignKey('sites.Site')

    class Meta:
        unique_together = ('challenge', 'site')

