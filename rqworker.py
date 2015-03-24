from app import redis
import settings
from raven import Client as Sentry
from rq import Queue, Worker, Connection
from rq.contrib.sentry import register_sentry


SENTRY = Sentry(settings.SENTRY_DSN)

with Connection(redis.connection):
    qs = [Queue('fad-tasks')]
    w = Worker(qs, default_result_ttl=0)
    # register_sentry(SENTRY, w)
    w.work()