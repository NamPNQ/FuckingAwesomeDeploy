from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app import db
from db.types.json import JSONEncodedDict


class Project(db.Model):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    repository_data = Column(JSONEncodedDict)
    project_data = Column(JSONEncodedDict)
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    @property
    def checks(self):
        return self.project_data.get('checks', [])

    @property
    def notifiers(self):
        return self.project_data.get('notifiers', [])

    @property
    def provider_config(self):
        return self.project_data.get('provider_config', {})

    @property
    def stages(self):
        return self.project_data.get('stages', [])


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
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_date = Column(DateTime)
    finished_date = Column(DateTime)

    @property
    def checks(self):
        return self.data.get('checks', [])

    @property
    def notifiers(self):
        return self.data.get('notifiers', [])

    @property
    def provider_config(self):
        return self.data.get('provider_config', {})

    @property
    def status_label(self):
        return STATUS_LABELS.get(int(self.status), 'unknown')

    @property
    def duration(self):
        if not self.date_finished:
            return
        return float('%.2f' % (self.date_finished - self.date_started).total_seconds())

    @property
    def log(self):
        return self.data.get('log', '')


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
    name = Column(String(200), nullable=False, unique=True)
    email = Column(String(200), nullable=False, unique=True)
    role = Column(Integer, nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow, nullable=False)

    @property
    def role_label(self):
        return UserRole_LABELS.get(int(self.role), 'Unknown')