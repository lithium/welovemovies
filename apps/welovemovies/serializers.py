from rest_framework import serializers


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
        for key in ('kind', 'year', 'title', 'cover url', 'genres', 'rating', 'plot outline'):
            representation[key.replace(' ','_')] = imdb_movie.get(key)
        return representation

