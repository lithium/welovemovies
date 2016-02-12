"""
Settings used for production
"""

DEBUG = False
DEBUG_ERRORS = False
DEBUG_STATIC = False
DEBUG_MEDIA = False


SECRET_KEY = ''
if not SECRET_KEY:
  raise RuntimeError("Must define a SECRET_KEY")
