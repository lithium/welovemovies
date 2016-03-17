import pprint
import traceback

from django.core.exceptions import ValidationError
from django.core.management import BaseCommand

from welovemovies.helpers import MongoHelper, TweetScraper
from welovemovies.models import Viewing


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--count', action='store', dest='count', default=20, help='How many tweets in total to process')

    def handle(self, *args, **options):
        self.verbosity = options.get('verbosity', 1)
        self.count = int(options.get('count', 20))

        mongo = MongoHelper()
        cursor = mongo.db.tweets.find({'$or': [{'processed': False, 'imported': False},
                                               {'processed': True,  'imported': False, 'processor_version': {'$lt': TweetScraper.VERSION}}
                                               ]})

        unparsed = mongo.db.tweets.find({'processed': True,  'imported': False, 'processor_version': {'$gte': TweetScraper.VERSION}})

        if self.verbosity:
            self.stdout.write("Found {} unprocessed tweets.  Skipping {}.  Processing at most {}:".format(cursor.count(), unparsed.count(), self.count))

        miss_count = 0
        imported_count = 0
        skipped_count = 0
        count = 0
        for row in cursor[:self.count]:
            tweet = row.get('tweet')
            txt = tweet.get('text')
            count += 1

            if self.verbosity > 1:
                title_match = TweetScraper.search_for_title(txt)
                self.stdout.write(u"\n{}".format(txt))
                pprint.pprint(title_match)

            if txt.startswith('RT'):
                skipped_count += 1
                self.stdout.write(u"Skip retweets.")
                continue

            try:
                viewing, created = Viewing.objects.get_or_create_from_tweet(tweet)
                if not viewing:
                    if self.verbosity > 1:
                        self.stdout.write(u"Unable to parse tweet.")
                    miss_count += 1
                else:
                    if created:
                        if self.verbosity > 1:
                            self.stdout.write(u"Imported tweet.")
                        imported_count += 1
                        row['imported'] = True
                    else:
                        if self.verbosity > 1:
                            self.stdout.write(u"Skipped.")
                        skipped_count += 1
            except ValidationError as e:
                traceback.print_exc()
                break
            else:
                row['processed'] = True
                row['processor_version'] = TweetScraper.VERSION
                mongo.db.tweets.save(row)

        if self.verbosity:
            self.stdout.write("Imported {count}.  Skipped {skip}.  Missed {miss}".format(count=imported_count,
                                                                                         miss=miss_count,
                                                                                         skip=skipped_count))

