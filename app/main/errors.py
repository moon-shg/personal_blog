from flask import render_template
from . import main


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@main.errorhandler(500)
def page_not_found(e):
    return render_template('errors/500.html'), 500


@main.errorhandler(403)
def page_not_found(e):
    return render_template('errors/403.html'), 403
