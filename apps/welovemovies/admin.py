from django.contrib import admin

from welovemovies.models import Movie


class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'year')
    search_fields = ('title', 'year', 'imdb_id', 'imdb_plot_outline')
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')
    fieldsets = (
        ("Metadata", {
            'fields': ('is_active', 'created_at', 'created_by', 'updated_at', 'updated_by'),
            'classes': ('collapse',)
        }),
        (None, {
            'fields': ('title', 'year', 'runtime'),
        }),
        ("IMDb", {
            'fields': ('imdb_id', 'imdb_plot_outline', 'imdb_rating', 'imdb_votes', 'cover_url', 'large_cover_url'),
        }),
    )

admin.site.register(Movie, MovieAdmin)