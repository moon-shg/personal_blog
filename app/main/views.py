from flask import render_template, redirect, url_for, request, current_app, flash
from . import main
from flask_login import current_user
from ..models import User, Role, Permission, Post, Category


# 主页面
@main.route('/', methods=['GET', 'POST'])
def index():
    # post 分页
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html', posts=posts, pagination=pagination)
