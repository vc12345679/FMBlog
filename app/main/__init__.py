#!/usr/bin/venv python3
# encoding=utf-8

__author__ = 'Siwei Chen<me@chensiwei.space'

from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
