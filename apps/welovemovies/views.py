from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.views.generic import ListView, DetailView, FormView

from welovemovies.forms import ScheduleViewingForm
from welovemovies.helpers import ImdbHelper
from welovemovies.models import Movie, Viewing
from welovemovies.serializers import ImdbResultsSerializer


class SearchResults(LoginRequiredMixin, ListView):
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


class MovieDetail(DetailView):
    model = Movie
    template_name = 'welovemovies/movie_detail.html'

    def get_object(self):
        movieID = self.kwargs.get('movieID')
        movie, created = Movie.cached.get_or_create(imdb_id=movieID)
        if created:
            movie.fetch_imdb()
        return movie


class ScheduleViewing(LoginRequiredMixin, MovieDetail, FormView):
    model = Movie
    form_class = ScheduleViewingForm
    http_method_names = ['post']

    def get_success_url(self):
        return reverse('movie_detail', kwargs={'movieID': self.kwargs.get('movieID')})

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        movie = self.get_object()
        scheduled_for = form.cleaned_data.get('scheduled_for')
        viewing, created = Viewing.cached.get_or_create(viewer=self.request.user, movie=movie)
        if scheduled_for:
            viewing.scheduled_for = scheduled_for
            viewing.save()
            messages.success(self.request, u"Scheduled to view on {}".format(viewing.scheduled_for.strftime("%b %d, %Y")))
        else:
            messages.success(self.request, u"Scheduled to view")
        return super(ScheduleViewing, self).form_valid(form)
