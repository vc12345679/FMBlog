#!/usr/bin/venv python3
# encoding=utf-8

__author__ = 'Siwei Chen<me@chensiwei.space'

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
from app import create_app, db

app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    manager.run()
