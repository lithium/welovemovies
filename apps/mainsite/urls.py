"""
Main URL Configuration 
"""

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView

from mainsite.views import HomePageView, error404, error500
from welovemovies.api_views import SiteViewingGraph, UserViewingGraph
from welovemovies.views import SearchResults, MovieDetail, ScheduleViewing, ViewingList, RecordViewing, MySchedule, \
    CachedCoverImage, RemoveViewing
from wlmuser.views import ProfileView, PublicProfile, PublicMovieList

handler404 = 'mainsite.views.error404'
handler500 = 'mainsite.views.error500'
urlpatterns = [
    # In production these should be served directly by http server
    url(r'^favicon\.png[/]?$', RedirectView.as_view(permanent=True, url='{}images/favicon.png'.format(settings.STATIC_URL))),
    url(r'^favicon\.ico[/]?$', RedirectView.as_view(permanent=True, url='{}images/favicon.png'.format(settings.STATIC_URL))),
    url(r'^robots\.txt$', RedirectView.as_view(permanent=True, url='{}robots.txt'.format(settings.STATIC_URL))),

    # Django Admin
    url(r'^staff/', include(admin.site.urls)),

    # allauth
    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/profile/$', ProfileView.as_view(), name='account_profile'),
    url(r'^profile/(?P<username>[^/]+)$', PublicProfile.as_view(), name='public_profile'),
    url(r'^profile/(?P<username>[^/]+)/movies$', PublicMovieList.as_view(), name='public_profile_movies'),

    # search results
    url(r'^search$', SearchResults.as_view(), name='search_results'),

    # rest api
    # url(r'^v1/search$', ImdbSearch.as_view(), name='api_imdb_search'),
    url(r'^v1/user/graph$', UserViewingGraph.as_view(), name='api_user_viewings'),
    url(r'^v1/graph$', SiteViewingGraph.as_view(), name='api_user_viewings'),

    # viewings
    url(r'^movies$', ViewingList.as_view(), name='my_movies'),
    url(r'^movie/(?P<movieID>[^/]+)$', MovieDetail.as_view(), name='movie_detail'),
    url(r'^movie/(?P<movieID>[^/]+)/schedule$', ScheduleViewing.as_view(), name='movie_schedule'),
    url(r'^movie/(?P<movieID>[^/]+)/record$', RecordViewing.as_view(), name='movie_record'),
    url(r'^movie/(?P<movieID>[^/]+)/cover$', CachedCoverImage.as_view(), name='movie_cover'),
    url(r'^viewing/(?P<pk>[^/]+)/remove$', RemoveViewing.as_view(), name='viewing_remove'),

    url(r'^schedule$', MySchedule.as_view(), name='my_schedule'),

    url(r'^$', HomePageView.as_view(), name='home'),
]




###
#
# Debugging Configuration
#
###


# Test URLs to allow you to see these pages while DEBUG is True
if getattr(settings, 'DEBUG_ERRORS', False):
    urlpatterns = [
        url(r'^error/404$', error404, name='error_404'),
        url(r'^error/500$', error500, name='error_500'),
    ] + urlpatterns

# If DEBUG_MEDIA is set, have django serve anything in MEDIA_ROOT at MEDIA_URL
if getattr(settings, 'DEBUG_MEDIA', True):
    from django.views.static import serve as static_serve
    media_url = getattr(settings, 'MEDIA_URL', '/media/').lstrip('/')
    urlpatterns = [
        url(r'^%s(?P<path>.*)$' % (media_url,), static_serve, {
            'document_root': settings.MEDIA_ROOT
        }),
    ] + urlpatterns

# If DEBUG_STATIC is set, have django serve up static files even if DEBUG=False
if getattr(settings, 'DEBUG_STATIC', True):
    static_url = getattr(settings, 'STATIC_URL', '/static/').lstrip('/')
    from django.contrib.staticfiles.views import serve as staticfiles_serve
    urlpatterns = [
        url(r'^%s(?P<path>.*)' % (static_url,), staticfiles_serve, kwargs={
            'insecure': True,
        })
    ] + urlpatterns
