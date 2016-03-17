import tweepy

from welovemovies.management.tweepycommand import TweepyCommand


class Command(TweepyCommand):
    help = 'Search for past tweet viewings'

    def add_arguments(self, parser):
        parser.add_argument('--count', action='store', dest='count', default=20, help='How many tweets in total to process')
        parser.add_argument('--query', action='store', dest='query', default='#dlmchallenge', help='the search query')
        parser.add_argument('--last', action='store', dest='last', default=-1, help='max_id to pass to twitter search')

    def handle_tweepy(self, *args, **options):
        query = options.get('query')

        try:
            max_tweets = int(options.get('count'))
        except ValueError:
            max_tweets = 20

        try:
            last_id = int(options.get('last'))
        except ValueError:
            last_id = -1

        api = tweepy.API(self.oauth_handler)

        if self.verbosity:
            self.stdout.write(u"Searching for {count} tweets matching '{query}' last_id={last}".format(**options))

        tweet_count = 0
        existing_count = 0
        while tweet_count < max_tweets:
            count = max_tweets - tweet_count
            try:
                new_tweets = api.search(q=query, count=count, max_id=str(last_id-1))
                if not new_tweets:
                    break
                for t in new_tweets:
                    if not self.store_tweet(t):
                        existing_count += 1
                    tweet_count += 1
                last_id = new_tweets[-1].id
            except tweepy.TweepError as e:
                break

        if self.verbosity:
            self.stdout.write(u"Found {}.  Skipped {}. last_id={}".format(tweet_count, existing_count, last_id))

