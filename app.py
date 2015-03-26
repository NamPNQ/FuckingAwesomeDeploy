# coding=utf-8
import json
import os
import hashlib
import logging
import flask
import urlparse
from flask import redirect, request, session, url_for, render_template, current_app, flash, abort, jsonify
from flask_redis import Redis
from flask_sqlalchemy import SQLAlchemy
from flask.ext.sse import sse
from raven.contrib.flask import Sentry

import assets
from constants import PROJECT_ROOT
from utils.auth import CurrentUser, login_required, role_required, get_current_user

# noinspection PyUnresolvedReferences
import settings

VERSION = (1, 0, 0)
__version__ = '.'.join(map(str, VERSION))

app = flask.Flask(
    __name__,
    static_folder=os.path.join(PROJECT_ROOT, 'static'),
    template_folder=os.path.join(PROJECT_ROOT, 'templates'))
app.register_blueprint(sse, url_prefix='/stream')

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


def gravatar_filter(email, size=100, rating='g', default='retro', force_default=False,
                    force_lower=False, use_ssl=False):
    if use_ssl:
        url = "https://secure.gravatar.com/avatar/"
    else:
        url = "http://www.gravatar.com/avatar/"
    if force_lower:
        email = email.lower()
    hashemail = hashlib.md5(email).hexdigest()
    link = "{url}{hashemail}?s={size}&d={default}&r={rating}".format(
        url=url, hashemail=hashemail, size=size,
        default=default, rating=rating)
    if force_default:
        link += "&f=y"
    return link

app.jinja_env.filters['gravatar'] = gravatar_filter
app.jinja_env.filters['alert_class'] = alert_class_filter
app.jinja_env.globals['current_user'] = CurrentUser()


import models
from models import UserRole

app.jinja_env.globals['Project'] = models.Project

if app.config['SENTRY_DSN'] and False:
    parsed = urlparse.urlparse(current_app.config['SENTRY_DSN'])
    dsn = '%s://%s@%s/%s' % (
        parsed.scheme.rsplit('+', 1)[-1],
        parsed.username,
        parsed.hostname + (':%s' % (parsed.port,) if parsed.port else ''),
        parsed.path,
    )
else:
    dsn = None

app.jinja_env.globals['SENTRY_PUBLIC_DSN'] = dsn
app.jinja_env.globals['VERSION'] = get_version()


# noinspection PyUnusedLocal
@app.before_request
def capture_user(*args, **kwargs):
    if 'uid' in session:
        sentry.client.user_context({
            'id': session['uid'],
            'email': session['email'],
        })


@app.before_request
def before_request():
    method = request.args.get('_method', '').upper()
    if method:
        request.environ['REQUEST_METHOD'] = method
        # noinspection PyProtectedMember
        ctx = flask._request_ctx_stack.top
        ctx.url_adapter.default_method = method
        assert request.method == method


@app.route('/', endpoint='index')
def index():
    user = get_current_user()
    if not user:
        return render_template('sessions/new.html', **{
            'body_class': 'sessions new'
        })

    import models
    return render_template('projects/index.html', **{
        'body_class': 'projects index',
        'projects': models.Project.query.all()
    })


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
    import requests
    from utils.auth import get_auth_flow

    authorized_url = 'authorized'
    complete_url = 'index'
    redirect_uri = url_for(authorized_url, _external=True)
    flow = get_auth_flow(redirect_uri=redirect_uri)
    resp = flow.step2_exchange(request.args['code'])
    data = requests.get('https://www.googleapis.com/userinfo/v2/me?access_token=%s' % resp.access_token).json()

    if current_app.config['GOOGLE_DOMAIN']:
        if data.get('hd') != current_app.config['GOOGLE_DOMAIN']:
            flash('Only #%s users are allowed to login' % current_app.config['GOOGLE_DOMAIN'], 'error')
            return redirect(url_for(complete_url))

    user = models.User.query.filter(
        models.User.email == data['email'],
    ).first()
    if user is None:
        user = models.User(email=data['email'], name=data['name'])
        db.session.add(user)
        db.session.flush()
        if user.id == 1:
            user.role = UserRole.admin
            db.session.add(user)
            db.session.flush()

    session['uid'] = user.id
    session['access_token'] = resp.access_token
    session['email'] = data['email']

    return redirect(url_for(complete_url))


@app.route('/projects/', endpoint='projects')
@login_required
def get_list_projects():
    return render_template('projects/index.html', **{
        'body_class': 'projects index',
        'projects': models.Project.query.all()
    })


@app.route('/projects/new', endpoint='new_project', methods=['GET', 'POST'])
@role_required([UserRole.admin])
def new_project():
    if request.method == 'GET':
        return render_template('projects/new.html', **{
            'body_class': 'projects new',
            'project': models.Project(name='')
        })
    elif request.method == 'POST':
        data = request.form
        name = data.get('name')
        description = data.get('description')
        repository_url = data.get('repository_url')
        repository_ssh_key = data.get('repository_ssh_key')
        project = models.Project(
            name=name,
            description=description,
            project_data={
                'stages': {
                    'production': {
                        'command': 'ls',
                        'locked': False,
                        'last_deploy': {
                            'id': 1,
                            'is_failed': True,
                            'short_reference': 'master'
                        }
                    },
                    'dev1': {
                        'command': 'python -c \'for _ in range(1000): print 1000\'',
                        'locked': False,
                        'last_deploy': {}
                    }
                }
            },
            repository_data={
                'url': repository_url,
                'ssh_key': repository_ssh_key
            }
        )
        db.session.add(project)
        db.session.flush()
        return redirect(url_for('project', project_id=project.id))


@app.route('/projects/<project_id>/', endpoint='project')
@login_required
def get_project(project_id):
    project = models.Project.query.filter(models.Project.id == project_id).first()
    if not project:
        return abort(404)
    if request.method == 'DELETE':
        user = get_current_user()
        if user.role != UserRole.admin:
            abort(403)
        db.session.delete(project)
        db.session.flush()
        return redirect(url_for('projects'))
    elif request.method == "GET":
        return render_template('projects/show.html', **{
            'body_class': 'projects show',
            'project': project})


@app.route('/projects/<project_id>/edit', endpoint='edit_project', methods=['GET', 'POST'])
@role_required([UserRole.admin])
def edit_project(project_id):
    project = models.Project.query.filter(models.Project.id == project_id).first()
    if not project:
        return abort(404)
    if request.method == 'POST':
        data = request.form
        name = data.get('name')
        description = data.get('description')
        repository_url = data.get('repository_url')
        repository_ssh_key = data.get('repository_ssh_key')
        project.name = name
        project.description = description
        project.repository_data = {
            'url': repository_url,
            'ssh_key': repository_ssh_key
        }
        db.session.add(project)
        db.session.flush()
        flash('Update success', 'success')
    return render_template('projects/edit.html', **{
        'body_class': 'projects edit',
        'project': project})


@app.route('/projects/<project_id>/stages', endpoint='project_stages')
@login_required
def project_stages(project_id):
    project = models.Project.query.filter(models.Project.id == project_id).first()
    if not project:
        return abort(404)
    return render_template('stages/index.html', **{
        'body_class': 'stages index',
        'project': project})


@app.route('/projects/<project_id>/stages/new',
           endpoint='new_project_stages', methods=['GET', 'POST'], defaults={'old_stage_name': None})
@app.route('/projects/<project_id>/stages/update/<old_stage_name>',
           endpoint='update_project_stages', methods=['GET', 'POST'])
@role_required([UserRole.admin])
def new_or_update_project_stages(project_id, old_stage_name):
    project = models.Project.query.filter(models.Project.id == project_id).first()
    if not project:
        return abort(404)
    if request.method == 'DELETE':
        if old_stage_name and old_stage_name in project.project_data['stages'].keys():
            project.project_data['stages'] = project.project_data['stages'].copy()
            del project.project_data['stages'][old_stage_name]
            db.session.add(project)
            db.session.flush()
        return redirect(url_for('project_stages', project_id=project.id))
    elif request.method == 'POST':
        json_data = json.loads(request.data)
        stage_name = json_data.get('name', None)
        stage_command = json_data.get('command', None)
        stage_locked = json_data.get('locked', False)
        if not stage_name or not stage_command:
            return jsonify({'status': 'failed'})
        project.project_data['stages'] = project.project_data['stages'].copy()
        if old_stage_name and old_stage_name in project.project_data['stages'].keys():
            del project.project_data['stages'][old_stage_name]
        project.project_data['stages'][stage_name] = {
            'command': stage_command,
            'locked': stage_locked
        }
        db.session.add(project)
        db.session.flush()
        return jsonify({'status': 'ok'})
    return render_template('stages/index.html', **{
        'body_class': 'stages index',
        'project': project})


@app.route('/projects/<project_id>/deploys', endpoint='project_deploys')
@login_required
def project_deploys(project_id):
    project = models.Project.query.filter(models.Project.id == project_id).first()
    if not project:
        return abort(404)
    deploys = models.Task.query.filter(models.Task.project_id == project_id).order_by(models.Task.created_date.desc())
    return render_template('deploys/index.html', **{
        'body_class': 'deploys index',
        'project': project,
        'deploys': deploys})


@app.route(
    '/projects/<project_id>/stages/<stage_name>/deploys/new',
    endpoint='new_project_deploy',
    methods=['GET', 'POST'])
def create_project_deploy(project_id, stage_name):
    project = models.Project.query.filter(models.Project.id == project_id).first()
    if not project:
        return abort(404)
    if request.method == 'GET':
        return render_template('deploys/new.html', **{
            'body_class': 'deploys new',
            'project': project})
    elif request.method == 'POST':
        from rq import Queue
        import vcs
        from utils.workspace import Workspace
        from utils.redis import lock
        from tasks import execute_task

        reference = request.form['reference']
        # TODO: Check param ref
        workspace = Workspace(
            path=project.get_path(),
        )

        vcs_backend = vcs.get(
            'git',
            url=project.repository_data['url'],
            workspace=workspace,
        )

        with lock(redis, 'repo:update:{}'.format(project.id)):
            vcs_backend.clone_or_update()

        with lock(redis, 'task:create:{}'.format(project.id), timeout=5):
            task = models.Task(
                project_id=project.id,
                stage=stage_name,
                name=models.TaskName.deploy,
                sha=reference,
                status=models.TaskStatus.pending,
                user_id=get_current_user().id,
                data={
                },
            )
            db.session.add(task)
            db.session.flush()
        q = Queue('fad-tasks', connection=redis.connection)
        q.enqueue(execute_task.execute_task, task.id)
        return redirect(url_for('project_deploy', project_id=project_id, deploy_id=task.id))


@app.route('/projects/<project_id>/deploys/<deploy_id>', endpoint='project_deploy')
def project_deploy(project_id, deploy_id):
    project = models.Project.query.filter(models.Project.id == project_id).first()
    if not project:
        return abort(404)
    deploy = models.Task.query.filter(models.Task.id == deploy_id).first()
    if not deploy:
        return abort(404)
    return render_template('deploys/show.html', **{
        'body_class': 'deploys show',
        'project': project,
        'deploy': deploy})


@app.route('/projects/<project_id>/webhooks', endpoint='project_webhooks')
@login_required
def project_webhooks(project_id):
    project = models.Project.query.filter(models.Project.id == project_id).first()
    if not project:
        return abort(404)
    return render_template('webhooks/index.html', **{
        'body_class': 'webhooks index',
        'project': project})


@app.route('/deploys/recent', endpoint='recent_deploys')
def recent_deploys():
    deploys = models.Task.query.order_by(models.Task.created_date.desc()).limit(10)
    return render_template('deploys/recent.html', **{
        'body_class': 'deploys recent',
        'deploys': deploys})


@app.route('/deploys/active', endpoint='active_deploys')
def active_deploys():
    deploys = models.Task.query.filter(models.Task.status == models.TaskStatus.in_progress)
    return render_template('deploys/active.html', **{
        'body_class': 'deploys active',
        'deploys': deploys})


@app.route('/admin/projects', endpoint='admin_projects')
@role_required([UserRole.admin])
def admin_projects():
    return render_template('admin/projects/show.html', **{
        'body_class': 'projects show',
        'projects': models.Project.query.all()
    })


@app.route('/admin/users', endpoint='admin_users', defaults={'user_id': None})
@app.route('/admin/users/<user_id>', endpoint='admin_users_edit', methods=['GET', 'POST'])
@role_required([UserRole.admin])
def admin_users(user_id):
    if request.method == 'POST':
        user = models.User.query.filter(models.User.id == user_id).first()
        role = json.loads(request.data).get('role', None)
        if not role:
            return jsonify({'status': 'failed'})
        if user:
            user.role = int(role)
            db.session.add(user)
            db.session.flush()
        return jsonify({'status': 'ok'})
    if user_id and request.method == "DELETE":
        user = models.User.query.filter(models.User.id == user_id).first()
        if user:
            db.session.delete(user)
            db.session.flush()
    return render_template('admin/users/index.html', **{
        'body_class': 'users index',
        'users': models.User.query.all(),
        'roles': models.UserRole_LABELS
    })