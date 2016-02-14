from django.contrib import admin

from challenge.models import Challenge, ActiveChallenge


class ActiveChallengeInline(admin.TabularInline):
    model = ActiveChallenge
    extra = 0
    fields = ('site',)


class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('name', 'how_many_movies', 'how_many_days', 'start', 'end')
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')
    fieldsets = (
        ("Metadata", {
            'fields': ('is_active', 'created_at', 'created_by', 'updated_at', 'updated_by'),
            'classes': ('collapse',)
        }),
        (None, {
            'fields': ('name', 'description'),
        }),
        ("Schedule", {
            'fields': ('start', 'end', 'how_many_movies'),
        }),
    )
    inlines = [
        ActiveChallengeInline
    ]


admin.site.register(Challenge, ChallengeAdmin)
