"""Production settings and globals."""
DEBUG_TOOLBAR_PATCH_SETTINGS = False

from base import *  # NOQA


########## SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = get_env_setting('SECRET_KEY')
########## END SECRET CONFIGURATION

DEBUG = False
