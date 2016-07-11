from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from django.views.generic import UpdateView, TemplateView, DetailView

from welovemovies.models import Viewing
from wlmuser.forms import ProfileForm
from wlmuser.models import WlmUser


class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'user/profile.html'
    form_class = ProfileForm
    model = WlmUser
    success_url = reverse_lazy('account_profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profile saved.")
        return super(ProfileView, self).form_valid(form)


class PublicProfile(DetailView):
    template_name = 'user/public_profile.html'
    model = WlmUser

    def get_object(self, queryset=None):
        try:
            return WlmUser.cached.get(username=self.kwargs.get('username'))
        except WlmUser.DoesNotExist:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super(PublicProfile, self).get_context_data(**kwargs)
        user = self.get_object()
        context.update({
            'user': user,
            'challenge': user.active_challenge(self.request),
        })
        return context


class PublicMovieList(PublicProfile):
    template_name = 'user/public_movies.html'

    def get_context_data(self, **kwargs):
        context = super(PublicMovieList, self).get_context_data(**kwargs)
        user = self.get_object()
        movies = sorted(user.watched_movies(), lambda a,b: cmp(b.viewed_on, a.viewed_on))
        loved_movies = filter(lambda v: v.rating == Viewing.RATING_LOVE, movies)
        liked_movies = filter(lambda v: v.rating == Viewing.RATING_LIKE, movies)
        hated_movies = filter(lambda v: v.rating == Viewing.RATING_HATE, movies)
        hateliked_movies = filter(lambda v: v.rating == Viewing.RATING_HATELIKE, movies)
        context.update({
            'movies': movies,
            'movie_count': user.watched_count,
            'loved_count': len(loved_movies),
            'liked_count': len(liked_movies),
            'hated_count': len(hated_movies),
            'hateliked_count': len(hateliked_movies)
        })
        return context
