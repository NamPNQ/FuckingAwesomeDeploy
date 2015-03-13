from __future__ import absolute_import, unicode_literals

from flask import request, session

from models import User

NOT_SET = object()
GOOGLE_AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_REVOKE_URI = 'https://accounts.google.com/o/oauth2/revoke'
GOOGLE_TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'

def get_auth_flow(redirect_uri=None):
    # XXX(dcramer): we have to generate this each request because oauth2client
    # doesn't want you to set redirect_uri as part of the request, which causes
    # a lot of runtime issues.
    auth_uri = GOOGLE_AUTH_URI
    if current_app.config['GOOGLE_DOMAIN']:
        auth_uri = auth_uri + '?hd=' + current_app.config['GOOGLE_DOMAIN']

    return OAuth2WebServerFlow(
        client_id=current_app.config['GOOGLE_CLIENT_ID'],
        client_secret=current_app.config['GOOGLE_CLIENT_SECRET'],
        scope='https://www.googleapis.com/auth/userinfo.email',
        redirect_uri=redirect_uri,
        user_agent='ds/{0} (python {1})'.format(
            freight.VERSION,
            sys.version,
        ),
        auth_uri=auth_uri,
        token_uri=GOOGLE_TOKEN_URI,
        revoke_uri=GOOGLE_REVOKE_URI,
    )


def get_current_user():
    """
    Return the currently authenticated user based on their active session.
    """
    if getattr(request, 'current_user', NOT_SET) is NOT_SET:
        if session.get('uid') is None:
            request.current_user = None
        else:
            request.current_user = User.query.get(session['uid'])
            if request.current_user is None:
                del session['uid']
    return request.current_user
