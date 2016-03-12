import logging

import tweepy
from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from welovemovies.models import Viewing


miss_logger = logging.getLogger('welovemovies.searchtweets.misses')
hit_logger = logging.getLogger('welovemovies.searchtweets.hits')


class Command(BaseCommand):
    help = 'Search for past tweet viewings'

    def add_arguments(self, parser):
        parser.add_argument('--count', action='store', dest='count', default=20, help='How many tweets in total to process')
        parser.add_argument('--query', action='store', dest='query', default='#dlmchallenge', help='the search query')
        parser.add_argument('--last', action='store', dest='last', default=-1, help='max_id to pass to twitter search')

    def handle(self, *args, **options):
        try:
            app = SocialApp.objects.get(provider='twitter')
        except SocialApp.DoesNotExist:
            raise CommandError("No twitter social app")

        token_key = getattr(settings, 'MANAGEMENT_TWITTER_TOKEN_KEY', None)
        token_secret = getattr(settings, 'MANAGEMENT_TWITTER_TOKEN_SECRET', None)
        if not (token_key and token_secret):
            raise CommandError("No MANAGEMENT_TWITTER_TOKEN in settings")

        auth = tweepy.OAuthHandler(app.client_id, app.secret)
        auth.set_access_token(token_key, token_secret)
        api = tweepy.API(auth)

        query = options.get('query')

        try:
            max_tweets = int(options.get('count'))
        except ValueError:
            max_tweets = 20

        try:
            last_id = int(options.get('last'))
        except ValueError:
            last_id = -1

        if options.get('verbosity') > 0:
            self.stdout.write(u"Searching for {count} tweets matching '{query}' last_id={last}".format(**options))

        tweet_count = 0
        while tweet_count < max_tweets:
            count = max_tweets - tweet_count
            try:
                new_tweets = api.search(q=query, count=count, max_id=str(last_id-1))
                if not new_tweets:
                    break
                for t in new_tweets:
                    self.process_tweet(t, options.get('verbosity'))
                    tweet_count += 1
                last_id = new_tweets[-1].id
            except tweepy.TweepError as e:
                break

        if options.get('verbosity') > 0:
            self.stdout.write(u"DONE.  last_id={}".format(last_id))

    def process_tweet(self, tweet, verbosity=1):
        viewing, created = Viewing.objects.get_or_create_from_tweet(tweet)
        if not viewing:
            msg = u"Unable to parse tweet. id=[{}] text=[{}]".format(tweet.id, tweet.text)
            miss_logger.error(msg)
            if verbosity > 1:
                self.stdout.write(msg)
        if viewing and created:
            msg = u"Imported tweet. id=[{}] text=[{}]".format(tweet.id, tweet.text)
            hit_logger.error(msg)
            if verbosity > 1:
                self.stdout.write(msg)

