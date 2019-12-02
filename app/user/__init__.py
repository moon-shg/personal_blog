from flask import Blueprint

user_page = Blueprint('user_page', __name__)

from . import views
