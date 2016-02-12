###
#
# Caching
#
###

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': None,
        'KEY_PREFIX': '',
        'VERSION': 1,
    }
}