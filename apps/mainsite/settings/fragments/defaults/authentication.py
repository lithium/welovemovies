###
#
# Authentication
#
###

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']
AUTH_USER_MODEL = 'auth.User'

LOGIN_REDIRECT_URL = '/accounts/profile/'
LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/logout/'