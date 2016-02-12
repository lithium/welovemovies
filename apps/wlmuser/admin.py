
from django.contrib import admin
from django.contrib.auth.models import Group

from wlmuser.models import ProxyGroup, WlmUser

admin.site.register(WlmUser)

admin.site.unregister(Group)
admin.site.register(ProxyGroup)