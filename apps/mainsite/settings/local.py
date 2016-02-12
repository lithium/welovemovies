"""
Default settings used for local development
"""

import os
from mainsite import TOP_DIR


DEBUG = True
DEBUG_ERRORS = True
DEBUG_STATIC = True
DEBUG_MEDIA = True

SECRET_KEY = '{{secret_key}}'



# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(TOP_DIR, 'db.sqlite3'),
    }
}


# Use django debug_toolbar if present
try:
  import debug_toolbar
  from defaults import MIDDLEWARE_CLASSES, INSTALLED_APPS
  MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES)
  INSTALLED_APPS = list(INSTALLED_APPS)
  MIDDLEWARE_CLASSES.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
  INSTALLED_APPS.append('debug_toolbar')
  INTERNAL_IPS = (
     '127.0.0.1',
  )
  DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS': False}
except ImportError:
  pass
