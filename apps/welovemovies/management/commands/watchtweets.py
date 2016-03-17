import tweepy

from welovemovies.management.tweepycommand import TweepyCommand


class Command(TweepyCommand, tweepy.StreamListener):
    help = 'Watch stream for tweet viewings'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        tweepy.StreamListener.__init__(self)

    def add_arguments(self, parser):
        parser.add_argument('--query', action='store', dest='query', default='#dlmchallenge', help='the search query')

    def handle_tweepy(self, *args, **options):
        query = options.get('query')

        self.existing_count = 0
        self.total_count = 0
        self.stream = tweepy.Stream(self.oauth_handler, self)

        if self.verbosity:
            self.stdout.write(u"Watching for tweets matching '{query}'".format(**options))

        try:
            self.stream.filter(track=[query])
        except KeyboardInterrupt:
            if self.verbosity:
                self.stdout.write(u"\nFound {} tweets. skipped {}.".format(self.total_count, self.existing_count))

    def on_status(self, status):
        if not self.store_tweet(status):
            self.existing_count += 1
        self.total_count += 1
        if self.verbosity:
            self.stdout.write(u"[{}] <@{}> {}".format(status.created_at, status.user.screen_name, status.text))
        return True

