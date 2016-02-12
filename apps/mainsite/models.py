import cachemodel
from django.db import models
from django.conf import settings


class ActiveModelManager(cachemodel.CacheModelManager):
    def get_queryset(self):
        qs = super(ActiveModelManager, self).get_queryset()
        return qs.filter(is_active=True)


class DefaultModel(cachemodel.CacheModel):
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_created', null=True, blank=True, on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_updated', null=True, blank=True, on_delete=models.SET_NULL)

    objects = models.Manager()
    active_objects = ActiveModelManager()

    class Meta:
        abstract = True
