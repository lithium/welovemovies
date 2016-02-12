from django.apps import AppConfig


class WlmUserAppConfig(AppConfig):
    name = 'wlmuser'
    verbose_name = 'Authentication'

default_app_config = 'wlmuser.WlmUserAppConfig'