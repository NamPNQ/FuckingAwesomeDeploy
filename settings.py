import os
from constants import PROJECT_ROOT

DEBUG = False

PROJECT_NAME = 'Fs Deploy Tool'

APPLICATION_ROOT = '/s3cret'

SECRET_KEY = 't\xad\xe7\xff%\xd2.\xfe\x03\x02=\xec\xaf\\2+\xb8=\xf7\x8a\x9aLD\xb1'

SSH_PRIVATE_KEY = ''

REDIS_URL = 'redis://191.236.82.114:9100'

WORKSPACE_ROOT = os.path.join(PROJECT_ROOT, 'tmp')

DEFAULT_TIMEOUT = 300

GOOGLE_CLIENT_ID = '903964971923-hhjld55spdvqmv24vl8kjft8q045e3pr.apps.googleusercontent.com'

GOOGLE_CLIENT_SECRET = 'lEv9Zf-tOAwjlWQY1gmAixAT'

# GOOGLE_DOMAIN = 'filestring.com'
GOOGLE_DOMAIN = ''

SQLALCHEMY_DATABASE_URI = 'sqlite:///fad_db.db'

SENTRY_DSN = ''

LOG_LEVEL = 'INFO'

SSE_REDIS_HOST = '191.236.82.114'
SSE_REDIS_PORT = '9100'
