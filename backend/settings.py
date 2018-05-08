# coding=utf-8
"""
Django settings for backend project.
Generated by 'django-admin startproject' using Django 1.8.17.
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'sq!f#iw20wk@lsd7p2j9#8hz&uqq8-_358&3=_6@i&$=2pe4ce'

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
DEBUG = False

ALLOWED_HOSTS = ['192.168.16.223', '127.0.0.1', '*']

# django-celery


# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'AppSimulator',
    # 'rest_framework',
    'corsheaders'
)

MIDDLEWARE_CLASSES = (
    # 'django.middleware.cache.UpdateCacheMiddleware',   # cache用
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django.middleware.security.SecurityMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',   # cache用
)

X_FRAME_OPTIONS = 'ALLOWALL'

CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    '*',
    'http://xgsj3-alpha.istarshine.com'
)

ROOT_URLCONF = 'backend.urls'

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
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        # 'rest_framework.renderers.XMLRenderer',
        'rest_framework.renderers.JSONRenderer',
        # 'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
}

SESSION_COOKIE_AGE = 60 * 60 * 4

CACHES = {
    'default': {
        # 'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        # 'LOCATION': 'unique-snowflake'
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}

# Internationalization
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale/'),)

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates'),]
TEMP_DIRS = os.path.join(BASE_DIR, 'static', 'AppSimulator', 'temp')
