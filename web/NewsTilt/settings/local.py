"""Settings file for local development of NT."""
from .base import *
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

INSTALLED_APPS += ['NewsTilt.NewsTiltApp']

ROOT_URLCONF = 'NewsTilt.urls'
WSGI_APPLICATION = 'NewsTilt.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'newstilt',
        'USER': 'postgres',
        'PASSWORD': 'cUkEtrE3',
        'HOST': 'localhost',
        'PORT': 5432,
        'ATOMIC_REQUESTS': True
    }
}

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'newstiltapi@gmail.com'
EMAIL_HOST_PASSWORD = 'ntapi2018'
EMAIL_PORT = 587
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'