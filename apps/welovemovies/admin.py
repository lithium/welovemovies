from django.contrib import admin
from django import forms
from django_object_actions import DjangoObjectActions

from welovemovies.models import Movie


class MovieAdminForm(forms.ModelForm):
    imdb_plot_outline = forms.CharField(widget=forms.Textarea(), required=False)

    class Meta:
        model = Movie
        fields = ('is_active',
                  'title', 'year', 'runtime',
                  'imdb_id', 'imdb_plot_outline', 'imdb_rating', 'imdb_votes', 'cover_url', 'large_cover_url')


class MovieAdmin(DjangoObjectActions, admin.ModelAdmin):
    objectactions = ('fetch_imdb',)

    list_display = ('title', 'year')
    search_fields = ('title', 'year', 'imdb_id', 'imdb_plot_outline')
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')
    form = MovieAdminForm
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

    def fetch_imdb(self, request, obj):
        obj.fetch_imdb()
    fetch_imdb.label = "Fetch IMDb"
    fetch_imdb.short_description = "Fetch information from IMDb"

admin.site.register(Movie, MovieAdmin)