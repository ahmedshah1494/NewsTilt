from django.core.management.base import BaseCommand, CommandError
import time
from web.NewsTilt.NewsTiltApp.tilt import *
from web.NewsTilt.NewsTiltApp.models import *
from web.NewsTilt.NewsTiltApp.constants import *

class Command(BaseCommand):
    help = 'Pulls articles from API'

    def handle(self, *args, **options):
        while True:
            print 'pulling articles'
            authors = Author.objects.all()
            for author in authors:
                recalculate_author_tilt(author)
            pubs = Publication.objects.all()
            for pub in pubs:
                recalculate_publication_tilt(pubs)
            time.sleep((3600) * HOURS_BW_AUTH_PUB_TILT_RECALC)
