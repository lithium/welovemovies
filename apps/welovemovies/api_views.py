import pytz
from django.contrib.sites.models import Site
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from mainsite.models import CachedSite
from welovemovies.helpers import ImdbHelper
from welovemovies.serializers import ImdbResultsSerializer, ViewingGraphSerializer
from wlmuser.models import WlmUser


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
    permission_classes = []

    def get(self, request, username):
        try:
            user = WlmUser.cached.get(username=username)
        except WlmUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        stats = user.viewing_graph(request)
        serializer = ViewingGraphSerializer(stats, context={'request': request,
                                                            'timezone': user.timezone})
        return Response(serializer.data)


class SiteViewingGraph(APIView):
    permission_classes = []

    def get(self, request):
        cached_site = CachedSite.objects.get_current(request)
        stats = cached_site.viewing_graph()
        tz = request.user.timezone if request.user.is_authenticated() else 'US/Pacific'
        serializer = ViewingGraphSerializer(stats, context={'request': request,
                                                            'timezone': tz})
        return Response(serializer.data)
