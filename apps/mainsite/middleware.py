import pytz
from django import http
from django.utils import timezone


class TrailingSlashMiddleware(object):
    def process_request(self, request):
        """Removes the slash from urls, or adds a slash for the admin urls"""
        if (request.path.startswith("/staff") or
            request.path.startswith("/accounts") or
            request.path.startswith("/__debug__")):
                if request.path[-1] != '/':
                    return http.HttpResponsePermanentRedirect(request.path+"/")
        else:
            if request.path != '/' and request.path[-1] == '/':
                return http.HttpResponsePermanentRedirect(request.path[:-1])
        return None


class TimezoneMiddleware(object):
    def process_request(self, request):
        tzname = request.user.timezone
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()
