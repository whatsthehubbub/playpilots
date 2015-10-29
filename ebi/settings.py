# Django settings for shohaiti project.

import socket
PRODUCTION = True

if 'corretto' in socket.gethostname() or 'ristretto' in socket.gethostname():
    PRODUCTION = False

DEBUG = True
if PRODUCTION:
    DEBUG = False

# DEBUG = True

TEMPLATE_DEBUG = DEBUG

INTERNAL_IPS = ('127.0.0.1')

ADMINS = (
    ('Alper Cugun', 'spam@example.com'),
)

MANAGERS = ADMINS


# Setup logging
import logging

if not PRODUCTION:
    logging.basicConfig(
        level = logging.DEBUG,
        format = '%(asctime)s %(levelname)s %(message)s',
    )
else:
    import os
    DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    logging.basicConfig(
        level = logging.DEBUG,
        format = '%(asctime)s %(levelname)s %(message)s',
        filename = os.path.join(DIR, 'logs', 'logfile.log'),
        filemode = 'a'
    )


if not PRODUCTION:
    DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    DATABASE_NAME = '/Users/alper/Documents/projects/play/site/sqlitedb'             # Or path to database file if using sqlite3.
    DATABASE_USER = ''             # Not used with sqlite3.
    DATABASE_PASSWORD = ''         # Not used with sqlite3.
else:
    DATABASE_ENGINE = 'mysql'
    DATABASE_NAME = 'ebi'
    DATABASE_USER = 'ebi'
    DATABASE_PASSWORD = ''
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.


# For debug turn off cache backend
# CACHE_BACKEND = 'file:///Users/alper/Documents/projects/sho/site/fscache'

if not PRODUCTION:
	CACHE_BACKEND = 'file:///Users/alper/Documents/projects/play/site/cache'
else:
    CACHE_BACKEND = 'memcached://127.0.0.1:11211/'


if not PRODUCTION:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Amsterdam'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'nl'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/Users/alper/Documents/projects/play/site/media/'

if PRODUCTION:
    MEDIA_ROOT = '/home/alper/ebi/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

AUTH_PROFILE_MODULE = "metagame.Player"

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware'
)

ROOT_URLCONF = 'ebi.urls'

TEMPLATE_CONTEXT_PROCESSORS = ("django.core.context_processors.auth",
        "django.core.context_processors.debug",
        "django.core.context_processors.request", # Added for grappelli
        "django.core.context_processors.i18n",
        "django.core.context_processors.media",
        "ebi.metagame.context_processors.base"
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/Users/alper/Documents/projects/play/site/ebi/templates/', # Local template dir
    '/home/alper/ebi/ebi/templates/' # Production template dir
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'ebi.metagame',
    'ebi.battleroyale',
    'django.contrib.admin',
    'django.contrib.flatpages',
    'actstream',
    'socialregistration',
    'ebi.kipwip',
    'ebi.stereoscoop',
    'ebi.bandjesland'
)


# Settings for social registration

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend', 
                        'socialregistration.auth.TwitterAuth',
                        'socialregistration.auth.FacebookAuth')

# These are the keys for the OAuth authentication app
TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET_KEY = ''
TWITTER_REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
TWITTER_ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
TWITTER_AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'


FACEBOOK_API_KEY = ''
FACEBOOK_SECRET_KEY = ''

SOCIALREGISTRATION_GENERATE_USERNAME = True
