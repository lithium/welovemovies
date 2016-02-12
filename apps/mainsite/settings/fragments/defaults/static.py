
###
#
# Static Files
#
###

import os

from mainsite import TOP_DIR


STATIC_ROOT = os.path.join(TOP_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(TOP_DIR, 'breakdown', 'static'),
]
STATIC_URL = '/static/'
