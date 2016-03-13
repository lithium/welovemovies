import logging
import pprint

import tweepy
from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from welovemovies.helpers import TweetScraper
from welovemovies.models import Viewing


class TweepyCommand(BaseCommand):

    def __init__(self, *args, **kwargs):
        super(TweepyCommand, self).__init__(*args, **kwargs)
        self.miss_logger = logging.getLogger('welovemovies.searchtweets.misses')
        self.hit_logger = logging.getLogger('welovemovies.searchtweets.hits')

    def handle(self, *args, **options):
        self.verbosity = options.get('verbosity', 1)

        try:
            self.social_app = SocialApp.objects.get(provider='twitter')
        except SocialApp.DoesNotExist:
            raise CommandError("No twitter social app")

        self.token_key = getattr(settings, 'MANAGEMENT_TWITTER_TOKEN_KEY', None)
        self.token_secret = getattr(settings, 'MANAGEMENT_TWITTER_TOKEN_SECRET', None)
        if not (self.token_key and self.token_secret):
            raise CommandError("No MANAGEMENT_TWITTER_TOKEN in settings")

        self.oauth_handler = tweepy.OAuthHandler(self.social_app.client_id, self.social_app.secret)
        self.oauth_handler.set_access_token(self.token_key, self.token_secret)

        self.handle_tweepy(*args, **options)

    def handle_tweepy(self, *args, **options):
        raise NotImplementedError("Must implement a handle_tweepy method")

    def process_tweet(self, tweet, log_misses=True):
        if self.verbosity > 1:
            title_match = TweetScraper.search_for_title(tweet.text)
            self.stdout.write(u"\n{}".format(tweet.text))
            pprint.pprint(title_match)
        viewing, created = Viewing.objects.get_or_create_from_tweet(tweet)
        if not viewing:
            msg = u"Unable to parse tweet. id=[{}] text=[{}]".format(tweet.id, tweet.text.replace("\n","\\n"))
            if log_misses:
                self.miss_logger.error(msg)
            if self.verbosity > 1:
                self.stdout.write(msg)
        else:
            if created:
                msg = u"Imported tweet. id=[{}] text=[{}]".format(tweet.id, tweet.text.replace("\n", "\\n"))
                self.hit_logger.error(msg)
                if self.verbosity > 1:
                    self.stdout.write(msg)
            elif self.verbosity > 1:
                self.stdout.write("Skipped.")

