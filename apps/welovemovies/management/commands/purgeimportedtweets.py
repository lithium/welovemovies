from django.core.management import BaseCommand

from welovemovies.models import Viewing, MovieMetadata


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--dry-run", "-n", action='store_true', default=False)

    def handle(self, *args, **options):
        verbosity = options.get('verbosity', 1)
        dry_run = options.get('dry_run', False)

        viewings = Viewing.objects.filter(twitter_status_id__isnull=False)
        if verbosity:
            self.stdout.write(u"{} viewings with twitter_status_id not null".format(viewings.count()))
        for viewing in viewings:
            if verbosity:
                self.stdout.write(u" {}".format(viewing))
            if not dry_run:
                viewing.delete()

        shorts = MovieMetadata.objects.filter(key='genre', value='Short')
        if verbosity:
            self.stdout.write(u"{} movies with genre='Short'".format(shorts.count()))
        for short in shorts:
            if verbosity:
                self.stdout.write(u" {} http://www.imdb.com/title/tt{}".format(short.movie, short.movie.imdb_id))
            if not dry_run:
                short.movie.delete()
