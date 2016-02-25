import datetime
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers
from hashlib import md5


class ImdbResultsSerializer(serializers.Serializer):
    id = serializers.CharField()
    kind = serializers.CharField()
    year = serializers.IntegerField()
    title = serializers.CharField()

    def to_representation(self, imdb_movie):
        representation = {
            'id': imdb_movie.getID(),
            'url': "http://imdb.com/title/tt{}/".format(imdb_movie.getID()),
        }
        # cover_url = imdb_movie.get('cover url')
        # if cover_url:
        #     digest = md5(cover_url).hexdigest()
        #     representation['cover_url'] = "{}imdb/image/{}".format(settings.MEDIA_URL, digest)
        for key in ('kind', 'year', 'title', 'long imdb title'):
            representation[key.replace(' ','_')] = imdb_movie.get(key)
        return representation


def seconds_since_epoch(dt=None, epoch=None):
    if epoch is None:
        epoch = datetime.datetime(1970,1,1)
    if dt is None:
        dt = timezone.now()
    return (dt - epoch).total_seconds()


class ViewingGraphSerializer(serializers.Serializer):
    def to_representation(self, day_stats):
        representation = {}
        for k,v in day_stats.items():
            d = seconds_since_epoch(datetime.datetime.combine(k, datetime.datetime.min.time()))
            representation[int(d)] = len(v['viewings'])
        return representation
