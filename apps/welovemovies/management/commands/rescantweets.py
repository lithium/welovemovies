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

        total_count = 0
        hit_count = 0
        miss_count = 0
        skip_count = 0
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
                            if self.process_tweet(tweet, log_misses=False):
                                hit_count += 1
                            else:
                                skip_count += 1
                        else:
                            self.stdout.write(u"\n{}\nno title match.".format(msg))
                            miss_count += 1
                    else:
                        self.stdout.write(u"no line match?: {}".format(line))
                    total_count += 1

        print "Scanned {total} tweets. Skipped {skip}.  {hit} Hits.  {miss} misses.  {rate:0.2f}%".format(total=total_count,
                                                                                                     hit=hit_count,
                                                                                                     miss=miss_count,
                                                                                                     skip=skip_count,
                                                                                                     rate=(float(hit_count+skip_count)/total_count)*100)

