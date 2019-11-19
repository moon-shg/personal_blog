from . import auth
from flask import render_template, redirect, url_for


@auth.route('/login')
def login():
    return render_template('auth/login.html')
