import tweepy
from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from welovemovies.models import Viewing
import sys


class Command(BaseCommand):
    help = 'Search for past tweet viewings'

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

        query = '#dlmchallenge'
        max_tweets = 20

        tweet_count = 0
        last_id = -1
        while tweet_count < max_tweets:
          count = max_tweets - tweet_count
          try:
            new_tweets = api.search(q=query, count=count, max_id=str(last_id-1))
            if not new_tweets:
              break
            for t in new_tweets:
                self.process_tweet(t)
                tweet_count += 1
            last_id = new_tweets[-1].id
          except tweepy.TweepError as e:
            break

    def process_tweet(self, tweet):
        # print u"\n\n{}: {}".format(tweet.user.screen_name, tweet.text)
        viewing, created = Viewing.objects.get_or_create_from_tweet(tweet)
        # sys.exit()
        pass
