#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask.ext.script import Manager
from flask.ext.migrate import MigrateCommand, Migrate
from app import app, db
# noinspection PyUnresolvedReferences
import models

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
