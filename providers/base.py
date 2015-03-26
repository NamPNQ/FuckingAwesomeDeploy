__all__ = ['Provider']

from flask import current_app
from tempfile import NamedTemporaryFile


class Provider(object):
    name = None

    def get_default_options(self):
        return {
            'timeout': {},
        }

    def get_options(self):
        return {}

    def execute(self, workspace, task):
        raise NotImplementedError

    def get_ssh_key(self, task):
        if not task.project.repository_data['ssh_key']:
            return

        f = NamedTemporaryFile()
        f.write(task.project.repository_data['ssh_key'])
        f.flush()
        f.seek(0)

        return f
