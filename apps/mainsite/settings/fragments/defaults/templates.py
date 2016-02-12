
### 
#
# Templates
#
###
import os

from mainsite import TOP_DIR

TEMPLATES = [
    # Jinja2 Teplates: ./breakdown/templates/jinja/*
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [
            os.path.join(TOP_DIR, 'breakdown', 'jinja2'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'mainsite.template.jinja2_environment',
        },
    },

    # Django Templates: ./breakdown/templates/django/*
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(TOP_DIR, 'breakdown', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },

]