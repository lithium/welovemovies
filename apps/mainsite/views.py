from django.contrib.sites.models import Site
from django.http import HttpResponseServerError, HttpResponseNotFound
from django.template import loader
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic.base import TemplateView

from challenge.models import ActiveChallenge
from mainsite.models import CachedSite


@xframe_options_exempt
def error404(request):
    try:
        template = loader.get_template('error/404.html')
    except TemplateDoesNotExist:
        return HttpResponseServerError('<h1>Page not found (404)</h1>', content_type='text/html')
    return HttpResponseNotFound(template.render())


@xframe_options_exempt
def error500(request):
    try:
        template = loader.get_template('error/500.html')
    except TemplateDoesNotExist:
        return HttpResponseServerError('<h1>Server Error (500)</h1>', content_type='text/html')
    return HttpResponseServerError(template.render())


class HomePageView(TemplateView):
    template_name = 'homepage/index.html'

    def active_challenge(self):
        site = Site.objects.get_current(self.request)
        active = ActiveChallenge.cached.get(site=site)
        return active.challenge

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context.update({
            'challenge': self.active_challenge(),
            'cached_site': CachedSite.objects.get_current(self.request),
        })
        return context

