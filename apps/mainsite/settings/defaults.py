"""
Default Django settings for the project.
"""

import os
import sys
from mainsite import TOP_DIR

from .fragments import load_settings_fragment
settings_fragment = lambda f: globals().update(load_settings_fragment(f))


###
#
# Installed Apps
#
###

INSTALLED_APPS = (
    'django.contrib.sites',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # providers
    # 'allauth.socialaccount.providers.amazon',
    # 'allauth.socialaccount.providers.facebook',
    # 'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.twitter',


    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'wlmuser',
    'welovemovies',
)


###
#
# Miscellaneous
#
###

SITE_ID = 1

ROOT_URLCONF = 'mainsite.urls'

WSGI_APPLICATION = 'mainsite.wsgi.application'


###
#
# Internationalization / Localization
#
###

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


###
#
# Static Files
#
###

settings_fragment('static')


###
#
# Media Files
#
###
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(TOP_DIR, 'mediafiles')
ADMIN_MEDIA_PREFIX = STATIC_URL+'admin/'
settings_fragment('media')


##
#
#   Fixtures
#
##

settings_fragment('fixtures')



###
#
# Middleware
#
###

settings_fragment('middleware')


### 
#
# Templates
#
###

settings_fragment('templates')



### 
#
# Caching
#
###

settings_fragment('caches')


### 
#
# Databases
#
###

settings_fragment('databases')


### 
#
# Logging
#
###

settings_fragment('logging')


### 
#
# Authentication
#
###

settings_fragment('authentication')


### 
#
# Email
#
###

settings_fragment('email')
