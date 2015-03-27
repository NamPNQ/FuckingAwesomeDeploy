import os
from constants import PROJECT_ROOT

DEBUG = True

PROJECT_NAME = 'Fs Deploy Tool'

SECRET_KEY = 't\xad\xe7\xff%\xd2.\xfe\x03\x02=\xec\xaf\\2+\xb8=\xf7\x8a\x9aLD\xb1'

SSH_PRIVATE_KEY = ''

REDIS_URL = 'redis://host:port'

WORKSPACE_ROOT = os.path.join(PROJECT_ROOT, 'tmp')

DEFAULT_TIMEOUT = 300

GOOGLE_CLIENT_ID = 'google_client_id'

GOOGLE_CLIENT_SECRET = 'google_client_sercet'

GOOGLE_DOMAIN = ''

SQLALCHEMY_DATABASE_URI = 'sqlite:///fad_db.db'

SENTRY_DSN = ''

LOG_LEVEL = 'INFO'

SSE_REDIS_HOST = 'host'
SSE_REDIS_PORT = 'port'

