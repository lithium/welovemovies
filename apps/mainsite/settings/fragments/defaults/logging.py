###
#
# Logging
#
#
#
###

from mainsite import TOP_DIR
import os

LOG_DIR = os.path.join(TOP_DIR, "logs")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
    },
    'handlers': {
        'debuglog': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'debug.log'),
            'formatter': 'verbose',
        },
        'requestlog': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'request.log'),
            'formatter': 'verbose',
        },

        'missedtweets': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'missed-tweets.log'),
            'formatter': 'verbose',
        },
        'scrapedtweets': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'scraped-tweets.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        # 'django': {
        #     'handlers': ['debuglog'],
        #     'level': 'DEBUG',
        #     'propagate': True,
        # },
        'django.request': {
            'handlers': ['requestlog'],
            'level': 'WARN',
            'propagate': False,
        },

        'welovemovies.searchtweets.misses': {
            'handlers': ['missedtweets'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'welovemovies.searchtweets.hits': {
            'handlers': ['scrapedtweets'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
