from django_cron import CronJobBase, Schedule
from .scrapers import pull_from_all

from .tilt import recalculate_author_tilt, recalculate_publication_tilt
from .models import *
# class UpdateArticleFeed(CronJobBase):
#     """docstring for UpdateArticleFeed"""
#     RUN_EVERY_MINS = 2
#     schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
#     code = 'NewsTiltApp.update_article_feed'
        
#     def do():
#         print 'pulling articles'
#         pull_from_all(10, enroll=True)

# class UpdateAuthorPublicationTilts(CronJobBase):
#     RUN_EVERY_MINS = 2
#     schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
#     code = 'NewsTiltApp.update_tilts'

#     def do():
#         print 'updating author and publication tilts'
#         authors = Author.objects.all()
#         for author in authors:
#             recalculate_author_tilt(author)

#         pubs = Publication.objects.all()
#         for pub in pubs:
#             recalculate_publication_tilt(pub)

def update_article_feed():
        print 'pulling articles'
        pull_from_all(10, enroll=True)

def update_tilts():
        print 'updating author and publication tilts'
        authors = Author.objects.all()
        for author in authors:
            recalculate_author_tilt(author)

        pubs = Publication.objects.all()
        for pub in pubs:
            recalculate_publication_tilt(pub)
