
from django.contrib import admin
from django.contrib.auth.models import Group

from welovemovies.models import Viewing
from wlmuser.models import ProxyGroup, WlmUser


class ViewingInline(admin.TabularInline):
    model = Viewing
    fields = ('movie', 'status', 'viewed_on')
    extra = 0
    fk_name = 'viewer'


class WlmUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff',)
    list_filter = ('is_staff','is_active',)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    filter_horizontal = ('groups', 'user_permissions')
    fieldsets = (
        (None, {
            'fields': ('username', 'first_name', 'last_name', 'email', 'password')
        }),
        ('Access', {
            'fields': ('is_active', 'is_staff', 'is_superuser',)
        }),
        ('Activity', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
        ('Groups', {
            'fields': ('groups',),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': ('user_permissions',),
            'classes': ('collapse',)
        }),
    )
    inlines = [
        ViewingInline
    ]

    def delete_model(self, request, obj):
        for viewing in obj.viewing_set.all():
            viewing.delete()
        obj.delete()

admin.site.register(WlmUser, WlmUserAdmin)

admin.site.unregister(Group)
admin.site.register(ProxyGroup)
