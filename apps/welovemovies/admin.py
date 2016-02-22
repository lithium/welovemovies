from django.contrib import admin
from django import forms
from django_object_actions import DjangoObjectActions

from welovemovies.models import Movie, MovieMetadata, MovieCast, Person


class MovieAdminForm(forms.ModelForm):
    imdb_plot_outline = forms.CharField(widget=forms.Textarea(), required=False)

    class Meta:
        model = Movie
        fields = ('is_active',
                  'title', 'year', 'runtime',
                  'imdb_id', 'imdb_plot_outline', 'imdb_rating', 'imdb_votes', 'cover_url', 'large_cover_url')


class MovieMetadataInline(admin.TabularInline):
    model = MovieMetadata
    extra = 0
    fields = ('key', 'value', 'source', 'source_id')
    readonly_fields = ('key', 'value', 'source', 'source_id')


class MovieCastInline(admin.TabularInline):
    model = MovieCast
    extra = 0
    fields = ('person', 'role')
    readonly_fields = ('person',)


class MovieAdmin(DjangoObjectActions, admin.ModelAdmin):
    objectactions = ('fetch_imdb',)
    actions = ('fetch_imdb_bulk',)

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
    inlines = [
        MovieMetadataInline,
        MovieCastInline
    ]

    def fetch_imdb_bulk(self, request, qs):
        for obj in qs:
            obj.fetch_imdb()

    def fetch_imdb(self, request, obj):
        obj.fetch_imdb()
    fetch_imdb.label = "Fetch IMDb"
    fetch_imdb.short_description = "Fetch information from IMDb"

admin.site.register(Movie, MovieAdmin)


class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'imdb_id')
    search_fields = ('name', 'imdb_id')
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')
    fieldsets = (
        ("Metadata", {
            'fields': ('is_active', 'created_at', 'created_by', 'updated_at', 'updated_by'),
            'classes': ('collapse',)
        }),
        (None, {
            'fields': ('imdb_id', 'name'),
        }),
    )

admin.site.register(Person, PersonAdmin)
