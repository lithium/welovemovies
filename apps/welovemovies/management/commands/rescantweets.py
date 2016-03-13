import codecs
import re

import tweepy

from welovemovies.helpers import TweetScraper
from welovemovies.management.tweepycommand import TweepyCommand


class Command(TweepyCommand):
    missed_regex = re.compile(r' id=\[(?P<id>\d+)\] text=\[(?P<text>.*)\]', re.IGNORECASE)

    def add_arguments(self, parser):
        parser.add_argument('log_file', nargs='+', type=str)

    def handle_tweepy(self, *args, **options):
        api = tweepy.API(self.oauth_handler)

        for log_path in options.get('log_file'):
            with codecs.open(log_path, 'r', encoding='utf-8') as log_file:
                for line in log_file.readlines():
                    line_match = self.missed_regex.search(line)
                    if line_match:
                        values = line_match.groupdict()
                        msg = values.get('text')
                        title_match = TweetScraper.search_for_title(msg)
                        if title_match:
                            # movie = Movie.objects.get_from_title_match(title_match)
                            tweet = api.get_status(values.get('id'))
                            self.process_tweet(tweet, log_misses=False)
                        else:
                            self.stdout.write(u"\n{}\nno title match.".format(msg))
                    else:
                        self.stdout.write(u"no line match?: {}".format(line))

