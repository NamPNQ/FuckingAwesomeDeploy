import os
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

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
    def stages(self):
        return self.project_data.get('stages', {})

    @property
    def stages_data(self):
        stages = []
        data = self.project_data.get('stages', {})
        for k, v in data.iteritems():
            stages.append(Stage(self.id, k, **v))
        return stages

    def get_path(self):
        from flask import current_app
        return os.path.join(
            current_app.config['WORKSPACE_ROOT'], 'fad-repo-{}'.format(self.id)
        )


class Stage(object):
    def __init__(self, project_id, name, **kwargs):
        self.project_id = project_id
        self.name = name
        self.data = kwargs

    @property
    def last_deploy(self):
        deploy = Task.query.\
            filter(Task.project_id == self.project_id and Task.stage == self.name).\
            order_by(Task.created_date.desc()).first()
        return deploy

    def __getattr__(self, item):
        return self.data.get(item, None)


class LogChunk(db.Model):
    __tablename__ = 'logchunk'

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('task.id', ondelete="CASCADE"), nullable=False)
    # offset is sum(c.size for c in chunks_before_this)
    offset = Column(Integer, nullable=False)
    # size is len(text)
    size = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow, nullable=False)


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
    def status_label_class(self):
        return 'success' if int(self.status) in [TaskStatus.finished, TaskStatus.pending, TaskStatus.in_progress] else 'danger'

    @property
    def duration(self):
        if not self.date_finished:
            return
        return float('%.2f' % (self.date_finished - self.date_started).total_seconds())

    @property
    def output(self):
        queryset = db.session.query(
            LogChunk.text, LogChunk.offset, LogChunk.size
        ).filter(
            LogChunk.task_id == self.id,
        ).order_by(LogChunk.offset.asc())
        logchunks = list(queryset)
        return ''.join(l.text for l in logchunks)

    @property
    def active(self):
        return int(self.status) in [TaskStatus.pending, TaskStatus.in_progress]

    @property
    def is_failed(self):
        return int(self.status) == TaskStatus.failed

    @property
    def user(self):
        return User.query.filter(User.id == self.user_id).first()

    @property
    def project(self):
        return Project.query.filter(Project.id == self.project_id).first()

    @property
    def summary(self):
        return '%s deployed %s to %s' % (self.user.name, self.sha, self.stage)


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

    def can_deploy(self):
        return self.role in [UserRole.admin, UserRole.developer]