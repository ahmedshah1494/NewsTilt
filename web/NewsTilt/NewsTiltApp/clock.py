from apscheduler.schedulers.blocking import BlockingScheduler
from scrapers import pull_from_all
from constants import *
from rq import Queue
from worker import conn

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=1)
def timed_job():
    print 'pulling articles'
    q = Queue(connection=conn)
    result = q.enqueue(pull_from_all, (ARICLES_PER_PULL, True))