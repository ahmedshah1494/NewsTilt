"""Settings file for local development of NT."""
from .base import *
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': os.environ['postgres_pwd'],
        'HOST': 'localhost',
        'PORT': 5432,
        'ATOMIC_REQUESTS': True
    }
}
