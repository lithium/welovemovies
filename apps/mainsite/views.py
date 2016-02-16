from django.http import HttpResponseServerError, HttpResponseNotFound
from django.template import loader
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic.base import TemplateView


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



