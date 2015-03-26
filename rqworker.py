from redis import Redis
import settings
from raven import Client as Sentry
from rq import Queue, Worker, Connection
from rq.contrib.sentry import register_sentry

if settings.SENTRY_DSN:
    SENTRY = Sentry(settings.SENTRY_DSN)
else:
    SENTRY = None

with Connection(Redis.from_url(settings.REDIS_URL)):
    qs = [Queue('fad-tasks')]
    w = Worker(qs, default_result_ttl=0)
    if SENTRY:
        register_sentry(SENTRY, w)
    w.work()