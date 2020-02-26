"""
Django settings for pulseapi project.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
import sys
import dj_database_url
import environ
import logging.config

from urllib.parse import quote_plus

if sys.version_info < (3, 6):
    raise ValueError("Please upgrade to Python 3.6 or later")

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = environ.Path(__file__) - 1
root = app - 1

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
env = environ.Env(
    AUTH_STAFF_EMAIL_DOMAINS=(list, []),
    CORS_ORIGIN_REGEX_WHITELIST=(list, []),
    CORS_ORIGIN_WHITELIST=(list, []),
    CSRF_TRUSTED_ORIGINS=(list, []),
    DEBUG=(bool, False),
    DJANGO_LOG_LEVEL=(str, 'INFO'),
    HEROKU_APP_NAME=(str, ''),
    HEROKU_PR_NUMBER=(str, ''),
    HEROKU_BRANCH=(str, ''),
    PULSE_FRONTEND_HOSTNAME=(str, ''),
    SECRET_KEY=(str, ''),
    SSL_PROTECTION=(bool, False),
    USE_S3=(bool, False),
    GITHUB_TOKEN=(str, ''),
    SLACK_WEBHOOK_RA=(str, ''),
)

SSL_PROTECTION = env('SSL_PROTECTION')


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')
ALLOW_UNIVERSAL_LOGIN = env('ALLOW_UNIVERSAL_LOGIN', default=None)

# This needs to be a real domain for google auth purposes. As such,
# you may need to add a "127.0.0.1    test.example.com" to your
# host file, so that google's redirect works. This is the same
# domain you will be specifying in your Flow credentials, and
# associated client_secrets.json
ALLOWED_HOSTS = os.getenv(
    'ALLOWED_HOSTS',
    'test.example.com,localhost,network-pulse-api-staging.herokuapp.com,network-pulse-api-production.herokuapp.com'
).split(',')

HEROKU_APP_NAME = env('HEROKU_APP_NAME')
HEROKU_PR_NUMBER = env('HEROKU_PR_NUMBER')
HEROKU_BRANCH = env('HEROKU_BRANCH')


# Create a simple function to show Django Debug Toolbar on Review App
def show_toolbar(request):
    return request.user.is_staff


# Adding support for Heroku review app
if env('HEROKU_APP_NAME'):
    herokuReviewAppHost = env('HEROKU_APP_NAME') + '.herokuapp.com'
    ALLOWED_HOSTS.append(herokuReviewAppHost)
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': 'pulseapi.settings.show_toolbar',
    }


SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 31
SECRET_KEY = env('SECRET_KEY')

# Application definition
SITE_ID = 1

INSTALLED_APPS = list(filter(None, [
    'ajax_select',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'django.forms',
    'django_filters',
    'corsheaders',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',
    'rest_framework',
    'storages',
    'pulseapi.utility',
    'pulseapi.entries',
    'pulseapi.tags',
    'pulseapi.issues',
    'pulseapi.helptypes',
    'pulseapi.users',
    'pulseapi.profiles',
    'pulseapi.creators',
    # see INTERNAL_IPS for when this actually activates when DEBUG is set:
    'debug_toolbar' if DEBUG is True else None,
]))

MIDDLEWARE = list(filter(None, [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # see INTERNAL_IPS for when this actually activates when DEBUG is set:
    'debug_toolbar.middleware.DebugToolbarMiddleware' if DEBUG is True else None,
]))

# Whitelisting for the debug toolbar: it will not kick in except for when
# accessed through the following domains ("IP" is a white lie, here).
INTERNAL_IPS = [
    'localhost',
    '127.0.0.1',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
LOGIN_REDIRECT_URL = '/'
LOGIN_ALLOWED_REDIRECT_DOMAINS = env('LOGIN_ALLOWED_REDIRECT_DOMAINS', cast=list, default=[])
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = env('AUTH_EMAIL_REDIRECT_URL', default=LOGIN_REDIRECT_URL)
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/accounts/login/?next={next_url}'.format(
    next_url=quote_plus(ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL)
)
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
    'github': {
        'SCOPE': [
            'read:user',
            'user:email',
        ]
    },
}
ACCOUNT_ADAPTER = 'pulseapi.users.adapter.PulseAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'pulseapi.users.adapter.PulseSocialAccountAdapter'
SOCIALACCOUNT_STORE_TOKENS = False
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https' if SSL_PROTECTION is True else 'http'
AUTH_USER_MODEL = 'users.EmailUser'
AUTH_STAFF_EMAIL_DOMAINS = env('AUTH_STAFF_EMAIL_DOMAINS')
ACCOUNT_EMAIL_VERIFICATION = (
    'mandatory'
    if env('AUTH_REQUIRE_EMAIL_VERIFICATION', cast=bool, default=False)
    else 'optional'
)
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = True


# Email settings (currently used for auth email verification only)
EMAIL_VERIFICATION_FROM = env('EMAIL_VERIFICATION_FROM', default='webmaster@localhost')
DEFAULT_FROM_EMAIL = EMAIL_VERIFICATION_FROM
if env('USE_CONSOLE_EMAIL', cast=bool, default=True):
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = env('MAILGUN_SMTP_SERVER')
    EMAIL_PORT = env('MAILGUN_SMTP_PORT')
    EMAIL_HOST_USER = env('MAILGUN_SMTP_LOGIN')
    EMAIL_HOST_PASSWORD = env('MAILGUN_SMTP_PASSWORD')

ROOT_URLCONF = 'pulseapi.urls'

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'pulseapi.utility.context_processor.heroku_app_name_var',
            ],
        },
    },
]

WSGI_APPLICATION = 'pulseapi.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

DATABASE_URL = os.getenv('DATABASE_URL', False)

if DATABASE_URL is not False:
    DATABASES['default'].update(dj_database_url.config())


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'staticfiles'),
]


# API Versioning
# An ordered list of (<version key>, <version value>) tuples
# where <version key> is the key used to identify a particular version
# and <version value> is the value of the version that will be used in URLs
API_VERSION_LIST = [
    ('version_1', 'v1',),
    ('version_2', 'v2',),
    ('version_3', 'v3',),
]
DEFAULT_VERSION = 'version_1'
# A dictionary of api versions with the value of each version key being
# a version number
API_VERSIONS = dict(API_VERSION_LIST)
# A regex group to optionally capture a version in a url from the list of versions specified above
VERSION_GROUP = r'((?P<version>v\d+)/)?'


# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'pulseapi.versioning.PulseAPIVersioning',
    # Default to v1 if no version is specified in the URL
    # For e.g. /api/pulse/entries/ will default to /api/pulse/v1/
    'DEFAULT_VERSION': API_VERSIONS[DEFAULT_VERSION],
    'ALLOWED_VERSIONS': list(API_VERSIONS.values())
}

# CORS settings
# we want to restrict API calls to domains we know
CORS_ORIGIN_ALLOW_ALL = False

# we also want cookie data, because we use CSRF tokens
CORS_ALLOW_CREDENTIALS = True

# and we want origin whitelisting
CORS_ORIGIN_WHITELIST = env('CORS_ORIGIN_WHITELIST')

CORS_ORIGIN_REGEX_WHITELIST = env('CORS_ORIGIN_REGEX_WHITELIST')

CSRF_TRUSTED_ORIGINS = env('CSRF_TRUSTED_ORIGINS')
CSRF_COOKIE_HTTPONLY = env('CSRF_COOKIE_HTTPONLY', default=SSL_PROTECTION)
CSRF_COOKIE_SECURE = env('CSRF_COOKIE_SECURE', default=SSL_PROTECTION)
SECURE_BROWSER_XSS_FILTER = env('SECURE_BROWSER_XSS_FILTER', default=SSL_PROTECTION)
SECURE_CONTENT_TYPE_NOSNIFF = env('SECURE_CONTENT_TYPE_NOSNIFF', default=SSL_PROTECTION)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=SSL_PROTECTION)
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 31 * 6
SECURE_SSL_REDIRECT = env('SECURE_SSL_REDIRECT', default=SSL_PROTECTION)
SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE', default=SSL_PROTECTION)

# Heroku goes into an infinite redirect loop without this. So it's kind of necessary.
# See https://docs.djangoproject.com/en/1.10/ref/settings/#secure-ssl-redirect
if SSL_PROTECTION is True:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

X_FRAME_OPTIONS = "DENY"

# Frontend URL is required for the RSS and Atom feeds
PULSE_FRONTEND_HOSTNAME = env('PULSE_FRONTEND_HOSTNAME')

PULSE_CONTACT_URL = env('PULSE_CONTACT_URL', default='')

USE_S3 = env('USE_S3')

if USE_S3:
    # Use S3 to store user files if the corresponding environment var is set
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_CUSTOM_DOMAIN = env('AWS_S3_CUSTOM_DOMAIN')
    AWS_LOCATION = env('AWS_STORAGE_ROOT', default=None)
else:
    # Otherwise use the default filesystem storage
    MEDIA_ROOT = root('media/')
    MEDIA_URL = '/media/'

# Remove the default Django loggers and configure new ones
LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] %(message)s'
        }
    },
    'handlers': {
        'debug': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true'],
            'formatter': 'verbose'
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler'
        },
        'debug-error': {
            'level': 'ERROR',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['debug'],
            'level': 'DEBUG'
        },
        'django.server': {
            'handlers': ['debug'],
            'level': 'DEBUG',
        },
        'django.request': {
            'handlers': ['error'],
            'propagate': False,
            'level': 'ERROR'
        },
        'django.template': {
            'handlers': ['debug-error'],
            'level': 'ERROR'
        },
        'django.db.backends': {
            'handlers': ['debug-error'],
            'level': 'ERROR'
        },
    }
}
DJANGO_LOG_LEVEL = env('DJANGO_LOG_LEVEL')
logging.config.dictConfig(LOGGING)

# Review app slack bot
GITHUB_TOKEN = env('GITHUB_TOKEN')
SLACK_WEBHOOK_RA = env('SLACK_WEBHOOK_RA')
