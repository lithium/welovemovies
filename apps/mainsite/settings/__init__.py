import os
from defaults import *

ENVIRONMENT = os.getenv("DJANGO_ENVIRONMENT", "local")

if ENVIRONMENT == "production":
  from production import *
elif ENVIRONMENT == "staging":
  from staging import *
elif ENVIRONMENT == "local":
  from local import *

