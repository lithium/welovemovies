from hashlib import md5

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import Http404, HttpResponseRedirect
from django.utils import timezone
from django.views.generic import ListView, DetailView, FormView, TemplateView, UpdateView, RedirectView, DeleteView

from welovemovies.forms import ScheduleViewingForm, RecordViewingForm, ScheduleForm
from welovemovies.helpers import ImdbHelper
from welovemovies.models import Movie, Viewing, Schedule
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
        results = imdb.search_movie(q, full_detail=False)
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
            movie.fetch_imdb(max_cast=5)
        return movie

    def get_context_data(self, **kwargs):
        context = super(MovieDetail, self).get_context_data(**kwargs)
        viewing = None
        try:
            viewing = Viewing.cached.get(movie=self.get_object(), viewer=self.request.user)
        except Viewing.DoesNotExist:
            pass

        context.update({
            'viewing': viewing
        })
        return context


class ScheduleViewing(LoginRequiredMixin, MovieDetail, FormView):
    form_class = ScheduleViewingForm
    http_method_names = ['post', 'get']

    def get(self, request, *args, **kwargs):
        self.get_viewing()
        return HttpResponseRedirect(reverse('movie_detail', kwargs={'movieID': self.kwargs.get('movieID')}))

    def get_viewing(self):
        movie = self.get_object()
        viewing, created = Viewing.cached.get_or_create(viewer=self.request.user, movie=movie)
        return viewing

    def get_success_url(self):
        return reverse('movie_detail', kwargs={'movieID': self.kwargs.get('movieID')})

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        scheduled_for = form.cleaned_data.get('scheduled_for')
        viewing = self.get_viewing()
        if scheduled_for:
            viewing.scheduled_for = scheduled_for
            viewing.save()
            messages.success(self.request, u"Scheduled to view on {}".format(viewing.scheduled_for.strftime("%b %d, %Y")))
        else:
            messages.success(self.request, u"Scheduled to view")
        return super(ScheduleViewing, self).form_valid(form)


class RecordViewing(UpdateView):
    model = Viewing
    form_class = RecordViewingForm
    http_method_names = ['post', 'get']
    template_name = 'welovemovies/movie_record.html'

    def get_movie(self):
        movieID = self.kwargs.get('movieID')
        movie, created = Movie.cached.get_or_create(imdb_id=movieID)
        if created:
            movie.fetch_imdb(max_cast=0)
        return movie

    def get_initial(self):
        initial = super(RecordViewing, self).get_initial()
        viewing = self.get_object()
        initial['seen_before'] = (viewing.status == Viewing.STATUS_REWATCHED)
        return initial

    def get_object(self):
        movie = self.get_movie()
        viewing, created = Viewing.cached.get_or_create(viewer=self.request.user, movie=movie)
        return viewing

    def get_success_url(self):
        return reverse('movie_detail', kwargs={'movieID': self.kwargs.get('movieID')})

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super(RecordViewing, self).form_invalid(form)

    def form_valid(self, form):
        viewing = form.save(commit=False)
        seen_before = form.cleaned_data.get('seen_before')
        viewing.status = Viewing.STATUS_REWATCHED if seen_before else Viewing.STATUS_WATCHED
        if not viewing.viewed_on:
            viewing.viewed_on = timezone.now()
        viewing.save()
        return HttpResponseRedirect(self.get_success_url())


class ViewingList(LoginRequiredMixin, TemplateView):
    model = Viewing
    template_name = 'welovemovies/movies.html'

    def get_context_data(self, **kwargs):
        context = super(ViewingList, self).get_context_data(**kwargs)
        context.update({
            'viewing_list': self.request.user.cached_viewings(),
            'watched': self.request.user.watched_movies(),
            'unwatched': self.request.user.unwatched_movies(),
            'challenge': self.request.user.active_challenge(self.request),
            'schedule': self.request.user.cached_schedule(self.request),
        })
        return context


class MySchedule(LoginRequiredMixin, UpdateView):
    model = Schedule
    template_name = 'welovemovies/schedule.html'
    form_class = ScheduleForm
    success_url = reverse_lazy('my_schedule')

    def get_object(self, queryset=None):
        return self.request.user.cached_schedule(self.request)

    def get_context_data(self, **kwargs):
        context = super(MySchedule, self).get_context_data(**kwargs)
        context.update({
            'challenge': self.request.user.active_challenge(self.request),
            'schedule': self.request.user.cached_schedule(self.request),
            'movies_watched': self.request.user.watched_count,
        })
        return context


class CachedCoverImage(RedirectView):
    http_method_names = ['get']

    def get_redirect_url(self, *args, **kwargs):
        imdb = ImdbHelper()
        imdb_movie = imdb.get_movie(kwargs.get('movieID'))

        size = self.request.GET.get('size', '')

        if size == 'full':
            url = imdb_movie.get('full-size cover url')
        else:
            url = imdb_movie.get('cover url')

        if not url:
            return "{}images/cover-placeholder.png".format(settings.STATIC_URL)

        imdb.download_image(url)
        digest = md5(url).hexdigest()
        return "{}imdb/image/{}".format(settings.MEDIA_URL, digest)


class RemoveViewing(DeleteView):
    success_url = reverse_lazy('my_movies')

    def get_object(self, queryset=None):
        return Viewing.cached.get(pk=self.kwargs.get('pk'))

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)
