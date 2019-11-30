from flask import render_template, redirect, url_for, request, current_app, flash
from . import main
from flask_login import current_user
from ..models import User, Role, Permission, Post, Category
from sqlalchemy import extract, func, and_
from app import db

# 主页面
@main.route('/', methods=['GET', 'POST'])
def index():
    # post 分页
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    # post 日期归档
    # 关键在于返回两个元素是tuple的列表[(month, count)]，[(year, count)]
    month_posts = []
    year_posts = []
    month_archives = db.session.query(extract('year', Post.timestamp).label('year'),
                                extract('month', Post.timestamp).label('month'),
                                func.count('*')).group_by('year', 'month').order_by('year', 'month').all()

    year_archives = db.session.query(extract('year', Post.timestamp).label('year'),
                                      func.count('*')).group_by('year').order_by('year').all()
    for month_archive in month_archives:
        month_posts.append((month_archive[0], month_archive[1], month_archive[2]))
    for year_archive in year_archives:
        year_posts.append((year_archive[0], year_archive[1]))

    return render_template('index.html', posts=posts, year_posts=year_posts, month_posts=month_posts, pagination=pagination)
