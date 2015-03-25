import os
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app import db
from db.types.json import JSONEncodedDict


class Project(db.Model):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    description = Column(String(500), nullable=True)
    repository_data = Column(JSONEncodedDict)
    project_data = Column(JSONEncodedDict)
    created_date = Column(DateTime, default=datetime.utcnow)

    @property
    def stages_data(self):
        stages = []
        data = self.project_data.get('stages', [])
        for k, v in data.iteritems():
            stages.append(Stage(self.id, k, **v))
        return stages

    def get_path(self):
        from flask import current_app
        return os.path.join(
            current_app.config['WORKSPACE_ROOT'], 'fab-repo-{}'.format(self.id)
        )


class Stage(object):
    def __init__(self, project_id, name, **kwargs):
        self.project_id = project_id
        self.name = name
        self.data = kwargs

    @property
    def last_deploy(self):
        deploy = Task.query.filter(Task.project_id == self.project_id and Task.stage == self.name).first()
        return deploy

    def __getattr__(self, item):
        return self.data.get(item, None)


class TaskName(object):
    deploy = 'deploy'

    @classmethod
    def get_label(cls, status):
        return status

    @classmethod
    def label_to_id(cls, label):
        return getattr(cls, label)


class TaskStatus(object):
    unknown = 0
    pending = 1
    in_progress = 2
    finished = 3
    failed = 4
    cancelled = 5

    @classmethod
    def get_label(cls, status):
        return STATUS_LABELS[status]

    @classmethod
    def label_to_id(cls, label):
        return STATUS_LABELS_REV[label]


STATUS_LABELS = {
    TaskStatus.unknown: 'unknown',
    TaskStatus.pending: 'pending',
    TaskStatus.in_progress: 'in_progress',
    TaskStatus.finished: 'finished',
    TaskStatus.failed: 'failed',
    TaskStatus.cancelled: 'cancelled',
}
STATUS_LABELS_REV = {
    v: k for k, v in STATUS_LABELS.items()
}


class Task(db.Model):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id', ondelete="CASCADE"),
                        nullable=False)
    user_id = Column(Integer, ForeignKey('user.id', ondelete="CASCADE"),
                     nullable=False)
    name = Column(String(128), nullable=False, default=TaskName.deploy)
    sha = Column(String(128))
    stage = Column(String(64), nullable=False)
    status = Column(Integer, nullable=False)
    data = Column(JSONEncodedDict)
    created_date = Column(DateTime, default=datetime.utcnow)
    started_date = Column(DateTime)
    finished_date = Column(DateTime)

    @property
    def status_label(self):
        return STATUS_LABELS.get(int(self.status), 'unknown')

    @property
    def duration(self):
        if not self.date_finished:
            return
        return float('%.2f' % (self.date_finished - self.date_started).total_seconds())

    @property
    def output(self):
        return self.data.get('output', '')

    @property
    def active(self):
        return int(self.status) in [TaskStatus.pending, TaskStatus.in_progress]

    @property
    def is_failed(self):
        return int(self.status) == TaskStatus.failed


class UserRole(object):
    admin = 0
    developer = 1
    viewer = 2

    @classmethod
    def get_label(cls, status):
        return status

    @classmethod
    def label_to_id(cls, label):
        return getattr(cls, label)

UserRole_LABELS = {
    UserRole.admin: 'Admin',
    UserRole.developer: 'Developer',
    UserRole.viewer: 'Viewer'
}

UserRole_LABELS_REV = {
    v: k for k, v in STATUS_LABELS.items()
}


class User(db.Model):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False, unique=True)
    role = Column(Integer, nullable=False, default=UserRole.viewer)
    date_created = Column(DateTime, default=datetime.utcnow)

    @property
    def role_label(self):
        return UserRole_LABELS.get(int(self.role), 'Unknown')

    @property
    def is_admin(self):
        return self.role == UserRole.admin