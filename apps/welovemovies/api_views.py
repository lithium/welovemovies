from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from welovemovies.helpers import ImdbHelper
from welovemovies.serializers import ImdbResultsSerializer


class ImdbSearch(APIView):
    def get(self, request):
        """
        Search for movies with imdb
        """
        q = request.query_params.get('q','')
        if not q:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        imdb = ImdbHelper()
        results = imdb.search_movie(q)
        serializer = ImdbResultsSerializer(results, many=True, context={'request': request})

        return Response(serializer.data)
