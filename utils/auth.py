import sys
from flask import request, session, current_app, redirect, url_for, abort
from oauth2client.client import OAuth2WebServerFlow
from functools import wraps

NOT_SET = object()
GOOGLE_AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_REVOKE_URI = 'https://accounts.google.com/o/oauth2/revoke'
GOOGLE_TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'


def get_auth_flow(redirect_uri=None):
    from app import get_version
    # XXX(dcramer): we have to generate this each request because oauth2client
    # doesn't want you to set redirect_uri as part of the request, which causes
    # a lot of runtime issues.
    auth_uri = GOOGLE_AUTH_URI
    # if current_app.config['GOOGLE_DOMAIN']:
    #     auth_uri = auth_uri + '?hd=' + current_app.config['GOOGLE_DOMAIN']

    return OAuth2WebServerFlow(
        client_id=current_app.config['GOOGLE_CLIENT_ID'],
        client_secret=current_app.config['GOOGLE_CLIENT_SECRET'],
        scope='email profile',
        redirect_uri=redirect_uri,
        user_agent='fab/{0} (python {1})'.format(
            get_version(),
            sys.version,
        ),
        auth_uri=auth_uri,
        token_uri=GOOGLE_TOKEN_URI,
        revoke_uri=GOOGLE_REVOKE_URI,
    )


def get_current_user():
    from models import User
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


# noinspection PyMethodMayBeStatic,PyClassHasNoInit
class CurrentUser():
        def is_authenticated(self):
            return True if get_current_user() else False

        def __getattr__(self, item):
            if not self.is_authenticated():
                return None
            else:
                return getattr(get_current_user(), item)


def login_required(fn):
    @wraps(fn)
    def func(*args, **kwargs):
        if get_current_user():
            return fn(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return func


def role_required(roles):
    def decorator(fn):
        @wraps(fn)
        def func(*args, **kwargs):
            current_user = get_current_user()
            if current_user and current_user.role in roles:
                return fn(*args, **kwargs)
            else:
                return abort(403, 'Permission denied')
        return func
    return decorator