from django.contrib.auth.models import Group, AbstractUser


class WlmUser(AbstractUser):

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class ProxyGroup(Group):
    class Meta:
        proxy = True
        app_label = 'wlmuser'
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'