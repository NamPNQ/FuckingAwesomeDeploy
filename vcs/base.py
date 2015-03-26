import os
import os.path

from errors import CommandError


class UnknownRevision(CommandError):
    pass


class Vcs(object):
    def __init__(self, workspace, url, username=None):
        self.url = url
        self.username = username
        self.workspace = workspace

        self._path_exists = None

    @property
    def path(self):
        return self.workspace.path

    def run(self, command, capture=False, workspace=None, *args, **kwargs):
        if workspace is None:
            workspace = self.workspace

        if not self.exists(workspace=workspace):
            kwargs.setdefault('cwd', None)

        if capture:
            handler = workspace.capture
        else:
            handler = workspace.run

        rv = handler(command, *args, **kwargs)
        if isinstance(rv, basestring):
            return rv.strip()
        return rv

    def exists(self, workspace=None):
        if workspace is None:
            workspace = self.workspace
        return os.path.exists(workspace.path)

    def clone_or_update(self):
        if self.exists():
            self.update()
        else:
            self.clone()

    def clone(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def checkout(self, ref):
        raise NotImplementedError

    def describe(self, ref):
        """
        Given a `ref` return the fully qualified version.
        """
        raise NotImplementedError

    def get_default_revision(self):
        raise NotImplementedError
