"""
Django settings for bad_llama_games project.
"""

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates')

STATIC_PATH = os.path.join(BASE_DIR, 'static')


SECRET_KEY = '+qyvy(+&@@9qvllh6*s%qe(e53*_3y%5a)_t-w8ullbe_(b(-_'

DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'llamalandmine',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'bad_llama_games.urls'

WSGI_APPLICATION = 'bad_llama_games.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Templates

TEMPLATE_DIRS = (
    TEMPLATE_PATH,
)


# Static files (css, JavaScript, Images)

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    STATIC_PATH,
)


SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'badllamagames@gmail.com'
EMAIL_HOST_PASSWORD = 'llamalandmine'
EMAIL_PORT = 587
