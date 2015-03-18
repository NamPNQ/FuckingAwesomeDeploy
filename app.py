# coding=utf-8
import os
import logging
import flask
from flask import redirect, request, session, url_for, render_template, current_app, flash
from flask_redis import Redis
from flask_sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry
from constants import PROJECT_ROOT
import assets

# noinspection PyUnresolvedReferences
import settings

VERSION = (1, 0, 0)
__version__ = '.'.join(map(str, VERSION))

app = flask.Flask(
    __name__,
    static_folder=os.path.join(PROJECT_ROOT, 'static'),
    template_folder=os.path.join(PROJECT_ROOT, 'templates'))
db = SQLAlchemy(session_options={'autocommit': True})
redis = Redis()
sentry = Sentry(logging=True, level=logging.WARN)

app.config.from_object('settings')

logging.getLogger().setLevel(getattr(logging, app.config['LOG_LEVEL']))

sentry.init_app(app)
redis.init_app(app)
db.init_app(app)
assets.register_app(app)


def get_version():
    return __version__


# Bootstrap helpers
def alert_class_filter(category):
    # Map different message types to Bootstrap alert classes
    categories = {
        "message": "warning",
        "error": "danger"
    }
    return categories.get(category, category)

app.jinja_env.filters['alert_class'] = alert_class_filter


@app.before_request
def capture_user(*args, **kwargs):
    if 'uid' in session:
        sentry.client.user_context({
            'id': session['uid'],
            'email': session['email'],
        })


@app.route('/projects/')
def get_list_projects():
    pass


@app.route('/projects/<project_id>/')
def get_project(project_id):
    pass


@app.route('/tasks/')
def get_list_tasks():
    pass


@app.route('/tasks/<task_id>/')
def get_list_task(task_id):
    pass


@app.route('/tasks/<task_id>/log/')
def get_task_log(project_id):
    pass


@app.route('/auth/login/', endpoint='login')
def login():
    from utils.auth import get_auth_flow

    authorized_url = 'authorized'
    redirect_uri = url_for(authorized_url, _external=True)
    flow = get_auth_flow(redirect_uri=redirect_uri)
    auth_uri = flow.step1_get_authorize_url()
    return redirect(auth_uri)


@app.route('/auth/logout/')
def logout():
    complete_url = 'index'

    session.pop('uid', None)
    session.pop('access_token', None)
    session.pop('email', None)
    return redirect(url_for(complete_url))


@app.route('/auth/complete/', endpoint='authorized')
def authorized():
    from utils.auth import get_auth_flow
    from models import User

    authorized_url = 'authorized'
    complete_url = 'index'

    redirect_uri = url_for(authorized_url, _external=True)
    flow = get_auth_flow(redirect_uri=redirect_uri)
    resp = flow.step2_exchange(request.args['code'])

    if current_app.config['GOOGLE_DOMAIN']:
        if resp.id_token.get('hd') != current_app.config['GOOGLE_DOMAIN']:
            flash('Only #%s users are allowed to login' % current_app.config['GOOGLE_DOMAIN'], 'error')
            return redirect(url_for(complete_url))

    user = User.query.filter(
        User.name == resp.id_token['email'],
    ).first()
    print user
    if user is None:
        user = User(name=resp.id_token['email'])
        print user
        db.session.add(user)
        db.session.flush()
        print user.id

    session['uid'] = user.id
    session['access_token'] = resp.access_token
    session['email'] = resp.id_token['email']

    return redirect(url_for(complete_url))


@app.route('/', endpoint='index')
def index():
    import urlparse
    from utils.auth import get_current_user

    user = get_current_user()
    if not user:
        return render_template('sessions/new.html', body_class='sessions new')
        # return redirect(url_for('login'))

    if current_app.config['SENTRY_DSN'] and False:
        parsed = urlparse.urlparse(current_app.config['SENTRY_DSN'])
        dsn = '%s://%s@%s/%s' % (
            parsed.scheme.rsplit('+', 1)[-1],
            parsed.username,
            parsed.hostname + (':%s' % (parsed.port,) if parsed.port else ''),
            parsed.path,
        )
    else:
        dsn = None

    return render_template('index.html', **{
        'SENTRY_PUBLIC_DSN': dsn,
        'VERSION': get_version(),
    })
