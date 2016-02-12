from django.apps import AppConfig


class WlmUserAppConfig(AppConfig):
    name = 'wlmuser'
    verbose_name = 'Users'

default_app_config = 'wlmuser.WlmUserAppConfig'