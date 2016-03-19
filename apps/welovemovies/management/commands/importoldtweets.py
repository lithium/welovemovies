import csv

import time
import tweepy

from welovemovies.management.tweepycommand import TweepyCommand


class Command(TweepyCommand):
    help = 'Import tweets from GetOldtweets csv files'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str)
        parser.add_argument('--count', action='store', dest='count', default=None, help='How many tweets in total to process')
        parser.add_argument('--rate-limit', action='store', dest='rate_limit', default=180, help='Max rate limit/15min')

    def handle_tweepy(self, *args, **options):
        csv_path = options.get('csv_path')
        count = options.get('count', None)
        rate_limit = options.get('rate_limit', 180)
        self.stdout.write("csv: {}".format(csv_path))

        delay_in_sec = 900.0/rate_limit

        api = tweepy.API(self.oauth_handler)
        if self.verbosity:
            self.stdout.write(u"Importing from {}. Delaying {} secs to rate limit {}/15min".format(csv_path, delay_in_sec, rate_limit))

        imported_count = 0
        existing_count = 0
        try:
            with open(csv_path) as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                for row in reader:
                    tweet_id = row.get('id')
                    status = None
                    while status is None:
                        try:
                            status = api.get_status(id=tweet_id)
                            if not self.store_tweet(status):
                                existing_count += 1
                            imported_count += 1
                            if self.verbosity > 1:
                                self.stdout.write(u"[{}] <@{}> {}".format(status.created_at, status.user.screen_name, status.text))
                                self.stdout.write("Sleeping for {}secs...".format(delay_in_sec))
                            time.sleep(delay_in_sec)
                            if count is not None and imported_count >= count:
                                break
                        except tweepy.error.RateLimitError:
                            if self.verbosity:
                                self.stdout.write("Rate Limit Exceeded! Sleeping for 15min...")
                            time.sleep(900)

        except KeyboardInterrupt as e:
            pass

        if self.verbosity:
            self.stdout.write(u"Imported {}.  Skipped {}.".format(imported_count, existing_count))

