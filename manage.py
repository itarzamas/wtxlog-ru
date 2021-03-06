#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pprint
import sys
from os import path
from wtxlog import create_app, db, get_appconfig
from flask_script import Manager
from flask.ext.script.commands import ShowUrls, Clean
from flask import current_app
#,Command

from flask_migrate import Migrate, MigrateCommand
# выскакивает врнингс 
#/home/admin/.virtualenvs/wtxlog/local/lib/python2.7/site-packages/flask_admin/model/base.py:1324:
# UserWarning: Fields missing from ruleset: slug
# решение отсюда http://stackoverflow.com/questions/34091818/how-can-i-avoid-flask-admin-2-1-warning-userwarning-fields-missing-from-rulese

#import warnings
#warnings.filterwarnings('ignore', 'Fields missing from ruleset', UserWarning)


COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='wtxlog/*')
    COV.start()



# bae, sae, production, local(default)
app = create_app(os.getenv('APP_CONFIG') or str(get_appconfig()) or 'default')

manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('urls',ShowUrls())
manager.add_command('db', MigrateCommand)

@manager.command
def dumpconfig():
    "Dumps config"
    pprint.pprint(current_app.config)

@manager.command
def deploy():
    """Run deployment tasks."""
    from flask_migrate import upgrade
    from wtxlog.models import Role

    upgrade()
    db.create_all()

    # create user roles
    Role.insert_roles()


@manager.shell
def make_shell_context():
    from wtxlog.models import User, Role, Permission, Category, Tag, \
        Article, Topic, Link, FriendLink, Flatpage, Label, Redirect, Setting
    return dict(
        app=app, db=db, User=User, Role=Role, Permission=Permission,
        Category=Category, Tag=Tag, Article=Article, Topic=Topic,
        Link=Link, FriendLink=FriendLink, Flatpage=Flatpage,
        Label=Label, Redirect=Redirect, Setting=Setting
    )


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp', 'coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


if __name__ == '__main__':
     manager.run()
