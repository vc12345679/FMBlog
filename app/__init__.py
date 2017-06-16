#!/usr/bin/env python3
# encoding=utf-8

__author__ = 'Siwei Chen<me@chensiwei.space>'

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
import os

from config import config

db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.template_folder = os.path.join(os.path.abspath('themes'), app.config['FMBLOG_THEME'])
    moment = Moment()
    moment.init_app(app)
    config[config_name].init_app(app)
    db.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
