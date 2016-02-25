from django.contrib.sites.models import Site
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from mainsite.models import CachedSite
from welovemovies.helpers import ImdbHelper
from welovemovies.serializers import ImdbResultsSerializer, ViewingGraphSerializer


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


class UserViewingGraph(APIView):
    def get(self, request):
        """
        """
        stats = request.user.viewing_graph(request)
        serializer = ViewingGraphSerializer(stats, context={'request': request})
        return Response(serializer.data)


class SiteViewingGraph(APIView):
    def get(self, request):
        cached_site = CachedSite.objects.get_current(request)
        stats = cached_site.viewing_graph()
        serializer = ViewingGraphSerializer(stats, context={'request': request})
        return Response(serializer.data)
