from django.conf import settings
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
        cover_url = imdb_movie.get('cover url')
        if cover_url:
            digest = md5(cover_url).hexdigest()
            representation['cover_url'] = "{}imdb/image/{}".format(settings.MEDIA_URL, digest)
        for key in ('kind', 'year', 'title', 'long imdb title', 'genres', 'rating', 'plot outline'):
            representation[key.replace(' ','_')] = imdb_movie.get(key)
        return representation

