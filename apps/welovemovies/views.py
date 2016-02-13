from django.http import Http404
from django.views.generic import ListView

from welovemovies.helpers import ImdbHelper
from welovemovies.serializers import ImdbResultsSerializer


class SearchResults(ListView):
    template_name = 'welovemovies/search_results.html'
    allow_empty = False
    context_object_name = 'results'

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        if not q:
            return []

        imdb = ImdbHelper()
        results = imdb.search_movie(q)
        serializer = ImdbResultsSerializer(results, many=True, context={'request': self.request})
        return serializer.data

    def get_context_data(self, **kwargs):
        context = super(SearchResults, self).get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context
