from django.core.management.base import BaseCommand, CommandError

from apscheduler.schedulers.blocking import BlockingScheduler
from .scrapers import pull_from_all
from .constants import *
from rq import Queue
from worker import conn

sched = BlockingScheduler()

class Command(BaseCommand):
    help = 'Pulls articles from API'

    @sched.scheduled_job('interval', minutes=1)
    def handle(self, *args, **options):
        print 'pulling articles'
        q = Queue(connection=conn)
        result = q.enqueue(pull_from_all, (ARICLES_PER_PULL, True))