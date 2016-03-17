import datetime
import logging

import tweepy
from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from welovemovies.helpers import MongoHelper


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

    def store_tweet(self, tweet):
        tweet_id = tweet.id
        mongo = MongoHelper()
        existing_row = mongo.db.tweets.find_one({'tweet.id': tweet_id})
        if not existing_row:
            row = {
                'inserted_at': datetime.datetime.utcnow(),
                'processed': False,
                'imported': False,
                'tweet': tweet._json,
            }
            mongo.db.tweets.insert_one(row)
            return True
        return False


