#coding=utf-8

BITCOIN_SERVER_ADDR = 'localhost:8333'
BITCOIN_SERVER_USER = 'ee'
BITCOIN_SERVER_PASS = 'ee33'

BITCOIN_SERVER_URL = 'http://%s:%s@%s' % (BITCOIN_SERVER_USER, BITCOIN_SERVER_PASS, BITCOIN_SERVER_ADDR)

BITCOIN_WITHDRAW = True   # can withdraw
#~ BITCOIN_WITHDRAW = False   # cannot withdraw

import djcelery
djcelery.setup_loader()

BROKER_URL = 'django://'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

TOPIC_START_WEIGHT = 10**5
TOPIC_END_WEIGHT = 10**4
TOPIC_POST_COST = 10
TOPIC_EVENT_CLOSED_EMAILS = []

import decimal
TOPIC_SUBMITTED_COST = decimal.Decimal(0.0000001)

# max bet score per topic, in one or more times
TOPIC_MAX_BET_SCORE = 1

# when topic is completed, divide the profit to site and the topic submitter
SITE_WIN_RATE = 0.1
SUBMITTER_WIN_RATE = 0.1

DATE_FORMAT = 'n/j/y'
DATETIME_FORMAT = 'n/j/y H:i'

EMAIL_HOST = 'smtp.yeah.net'
EMAIL_HOST_USER = 'yuce_yuce@yeah.net'
EMAIL_HOST_PASSWORD = 'Yuce321'
EMAIL_PORT = 25
DEFAULT_FROM_EMAIL = 'yuce_yuce@yeah.net'


from os.path import dirname, join, abspath


ROOT = dirname(abspath(__file__))

LOCALE_PATHS = (
    join(dirname(ROOT), 'conf', 'locale'),
)

AUTH_USER_MODEL = 'core.User'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': join(ROOT, 'dev.db'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

import dj_database_url
DATABASES = {'default': dj_database_url.config()}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'zh-cn'
gettext_noop = lambda s: s
LANGUAGES = (
    ('en', gettext_noop('English')),
    ('zh-cn', gettext_noop(u'中文')),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

MEDIA_ROOT = join(ROOT, 'media')

MEDIA_URL = '/media/'

STATIC_ROOT = join(ROOT, 'static')

STATIC_URL = '/static/'

STATICFILES_DIRS = (
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'g*i8%1++w4qbhd&qtl^(hjw_w8x6yq5^cct6v1k)4t)_yq_g9y'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
)

ROOT_URLCONF = 'yuce.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'yuce.wsgi.application'

TEMPLATE_DIRS = (
    join(ROOT, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.admin',
    'gunicorn',
    'django_reset',
    'endless_pagination',
    'bootstrapform',
    'south',
    'registration',
    'captcha',
    'djcelery',
    'kombu.transport.django',
    'core',

    'task_tracker',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

try:
    from settings_local import *
except ImportError:
    pass
