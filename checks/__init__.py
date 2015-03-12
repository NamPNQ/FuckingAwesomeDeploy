from __future__ import absolute_import, unicode_literals

from .base import Check  # NOQA
from .manager import CheckManager
from .github import GitHubContextCheck

manager = CheckManager()
manager.add('github', GitHubContextCheck)

get = manager.get
