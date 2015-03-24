from errors import CommandError
from .base import UnknownRevision  # NOQA
from .manager import VcsManager
from .git import GitVcs

manager = VcsManager()
manager.add('git', GitVcs)

get = manager.get


# def get(*args, **kwargs):
#     from .manager import VcsManager
#     from .git import GitVcs
#     manager = VcsManager()
#     manager.add('git', GitVcs)
#     from .manager import VcsManager
#     return manager.get(*args, **kwargs)