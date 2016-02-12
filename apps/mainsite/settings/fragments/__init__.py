import importlib
import os
import sys
from mainsite import TOP_DIR

__all__ = ["load_settings_fragment"]


#
# Using Setting Fragments:
#       
#       from mainsite.settings.fragments import load_settings_fragment
#       settings_fragment = lambda fragment_name: globals().update(load_settings_fragment(fragment_name))
#       settings_fragment('logging')
#
# This will attempt to locate the fragment in the following order:
#    ./settings_fragments/<environment>/logging.py
#    ./settings_fragments/defaults/logging.py
#    ./apps/mainsite/settings/fragments/<environment>/logging.py
#    ./apps/mainsite/settings/fragments/defaults/logging.py



# Make sure our default settings_fragments are available
FRAGMENT_SETTINGS_DIR = os.path.join(TOP_DIR, 'apps', 'mainsite', 'settings', 'fragments')
sys.path.insert(0, FRAGMENT_SETTINGS_DIR)


# If any deployment overrides existing at ./settings_fragments load those first
FRAGMENT_OVERRIDES_DIR = os.path.join(TOP_DIR, 'settings_fragments')
if os.path.exists(FRAGMENT_OVERRIDES_DIR):
    sys.path.insert(0, FRAGMENT_OVERRIDES_DIR)


def load_settings_fragment(fragment_name, package=None):
    """
    Load a settings fragment either based on the django environment, or from default fragment
    """

    django_environment = os.getenv("DJANGO_ENVIRONMENT", "local")

    environment_fragment_name = '{}.{}'.format(django_environment, fragment_name) 
    try:
        fragment = importlib.import_module(environment_fragment_name, package=package)
    except ImportError as e:
        try:
            fragment = importlib.import_module('defaults.{}'.format(fragment_name), package=package)
        except ImportError as e:
            raise ImportError("Could not load settings fragment '{}' for environment '{}'".format(fragment_name, django_environment))

    return fragment.__dict__
    # Hack all references in fragment into the local namespace
    # globals().update(fragment.__dict__)


