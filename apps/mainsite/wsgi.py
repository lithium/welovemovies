"""
WSGI config for standard18 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application


APPS_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if APPS_DIR not in sys.path:
    sys.path.insert(0, APPS_DIR)

os.environ["DJANGO_SETTINGS_MODULE"] = "mainsite.settings"

application = get_wsgi_application()
