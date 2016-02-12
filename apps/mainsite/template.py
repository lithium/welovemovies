from allauth.socialaccount import providers
from allauth.socialaccount.templatetags.socialaccount import provider_login_url
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse
from jinja2 import Environment

__all__ = ["environment"]


def jinja2_environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'reverse': reverse,
        'get_social_providers': providers.registry.get_list,
    })
    return env
