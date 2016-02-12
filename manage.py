#!/usr/bin/env python
import os
import sys


# assume 'apps' is a directory with same parent directory as this file 
APPS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'apps'))
if APPS_DIR not in sys.path:
    sys.path.insert(0, APPS_DIR)


if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = "mainsite.settings"

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)