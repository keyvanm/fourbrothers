"""
Django settings for fourbrothers project.

Generated by 'django-admin startproject' using Django 1.8.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
if 'DJANGO_DEBUG' in os.environ:
    DEBUG = (os.environ['DJANGO_DEBUG'] == "True")

ALLOWED_HOSTS = []

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%sez1v1@)hi-$b6la@wjc-zq6kp=!bbxk!*7emy8k6y&tgr^ij'

# Application definition

INSTALLED_APPS = (
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    #
    'storages',
    's3_folder_storage',
    'collectfast',
    #
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    #
    'bootstrap3',
    'bootstrapform',
    'django_extensions',
    'bootstrap3_datetime',
    #
    'user_manager',
    'appt_mgmt',
    'dashboard',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

ROOT_URLCONF = 'fourbrothers.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

BOOTSTRAP3 = {
    'javascript_in_head': True,
}

LOGIN_REDIRECT_URL = '/'
# Django all auth settings
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_DISPLAY = lambda user: user.get_full_name()
ACCOUNT_EMAIL_VERIFICATION = "optional"
if DEBUG:
    ACCOUNT_EMAIL_VERIFICATION = "none"

ACCOUNT_EMAIL_SUBJECT_PREFIX = "FourBrothers - "
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_SIGNUP_FORM_CLASS = "user_manager.forms.MySignupForm"

SITE_ID = 1

WSGI_APPLICATION = 'fourbrothers.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

if 'RDS_DB_NAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
        }
    }
else:
    # sqlite is the quick an easy development db
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3')
        }
    }

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'indie_static'),
)
if 'AWS_STORAGE_BUCKET_NAME' in os.environ:
    COLLECTFAST_ENABLED = True
    DEFAULT_FILE_STORAGE = 's3_folder_storage.s3.DefaultStorage'
    DEFAULT_S3_PATH = "media"
    STATICFILES_STORAGE = 's3_folder_storage.s3.StaticStorage'
    STATIC_S3_PATH = "static"
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_KEY']
    AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']

    MEDIA_ROOT = '/%s/' % DEFAULT_S3_PATH
    MEDIA_URL = '//%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME
    STATIC_ROOT = "/%s/" % STATIC_S3_PATH
    STATIC_URL = '//%s.s3.amazonaws.com/static/' % AWS_STORAGE_BUCKET_NAME
    ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
    AWS_PRELOAD_METADATA = True
else:
    COLLECTFAST_ENABLED = False

# HTTPS Security
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# if DEBUG:
#     EMAIL_HOST = '127.0.0.1'
#     EMAIL_HOST_USER = ''
#     EMAIL_HOST_PASSWORD = ''
#     EMAIL_PORT = 1025
#     EMAIL_USE_TLS = False

# Email
if 'EMAIL_HOST_USER' in os.environ:
    EMAIL_USE_TLS = True
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Stripe settings
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "sk_test_ozBjcexqlj2ZBUp6VRkB8yyP")
STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY", "pk_test_2EZfjLSASrilnHsWADe0pOSP")
if DEBUG:
    STRIPE_SECRET_KEY = "sk_test_ozBjcexqlj2ZBUp6VRkB8yyP"
    STRIPE_PUBLIC_KEY = "pk_test_2EZfjLSASrilnHsWADe0pOSP"


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Toronto'

USE_I18N = True

USE_L10N = True

USE_TZ = True


MAX_NUM_APPT_TIME_SLOT = 1

# Secret key for prod server
SECRET_KEY = os.environ.get('SECRET_KEY')


# local settings
try:
    from local_settings import *
except ImportError, e:
    pass

try:
    assert SECRET_KEY
except (NameError, AssertionError):
    from secret_key_gen import SECRET_KEY
