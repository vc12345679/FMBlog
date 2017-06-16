#!/usr/bin/env python3
# encoding=utf-8

__author__ = 'Siwei Chen<me@chensiwei.space>'

from flask import render_template, current_app
from . import main


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html', e=str(e), site=current_app.config['FMBLOG_SITE']), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('50x.html', e=str(e), site=current_app.config['FMBLOG_SITE']), 500
