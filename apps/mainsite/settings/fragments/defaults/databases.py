
###
#
# Databases
#
#    https://docs.djangoproject.com/en/1.8/ref/settings/#databases
#
###
import os

from mainsite import TOP_DIR

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(TOP_DIR, 'db.sqlite3'),
    }
}
