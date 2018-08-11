DEBUG = False

DATABASE_URL = os.environ['DATABASE_URL']

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'newstiltapi@gmail.com'
EMAIL_HOST_PASSWORD = 'ntapi2018'
EMAIL_PORT = 587
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

CRONJOBS = [
    ('*/2 * * * *', 'NewsTilt.NewsTiltApp.cron.UpdateArticleFeed'),
    ('*/2 * * * *', 'NewsTilt.NewsTiltApp.cron.UpdateAuthorPublicationTilts'),
]