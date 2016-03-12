import logging

import tweepy

from welovemovies.management.tweepycommand import TweepyCommand

miss_logger = logging.getLogger('welovemovies.searchtweets.misses')
hit_logger = logging.getLogger('welovemovies.searchtweets.hits')


class TweetListener(tweepy.StreamListener):

    def __init__(self, handle_status, *args, **kwargs):
        super(TweetListener, self).__init__(*args, **kwargs)
        if not callable(handle_status):
            raise ValueError("handle_status must be a callable")
        self.handle_status = handle_status

    def on_status(self, status):
        print(status)
        self.handle_status(status)
        return True


class Command(TweepyCommand):
    help = 'Watch stream for tweet viewings'

    def add_arguments(self, parser):
        parser.add_argument('--query', action='store', dest='query', default='#dlmchallenge', help='the search query')

    def handle_tweepy(self, *args, **options):
        query = options.get('query')

        self.stream = tweepy.Stream(self.oauth_handler, TweetListener(self.process_tweet))

        if self.verbosity:
            self.stdout.write(u"Watching for tweets matching '{query}'".format(**options))

        self.stream.filter(track=[query])
