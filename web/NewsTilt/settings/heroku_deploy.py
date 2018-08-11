from .base import *
import dj_database_url
import os 

SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = False

INSTALLED_APPS += ['web.NewsTilt.NewsTiltApp',]

ROOT_URLCONF = 'web.NewsTilt.NewsTiltApp.urls'
WSGI_APPLICATION = 'web.NewsTilt.wsgi.application'

DATABASES = {}
DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'newstiltapi@gmail.com'
EMAIL_HOST_PASSWORD = 'ntapi2018'
EMAIL_PORT = 587
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

CRONJOBS = [
    ('*/2 * * * *', 'web.NewsTilt.NewsTiltApp.cron.UpdateArticleFeed'),
    ('*/2 * * * *', 'web.NewsTilt.NewsTiltApp.cron.UpdateAuthorPublicationTilts'),
]