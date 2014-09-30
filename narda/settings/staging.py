"""Production settings and globals."""
DEBUG_TOOLBAR_PATCH_SETTINGS = False

from base import *  # NOQA

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'elbambi_narda_staging',
    }
}

DEBUG = False
