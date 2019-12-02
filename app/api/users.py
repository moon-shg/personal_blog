from . import api
from app.models import User, Permission, Post
from flask import g, jsonify, request, current_app, url_for
from .errors import forbidden


# 获取用户
@api.route('/user/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    # 只允许用户本人或管理员获得用户资料
    if g.current_user != user or not g.current_user.can(Permission.ADMIN):
        return forbidden('Insufficient permission')
    return jsonify(user.to_json())


# 返回一个用户发布的所有博客文章
@api.route('/user/<int:id>/posts/')
def get_user_posts(id):
    user = User.query.get_or_404(id)
    # 分页
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.paginate(page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_posts', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_posts', page=page+1)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev_url': prev,
        'next_url': next,
        'count': pagination.total
    })

# 返回一个用户收藏的所有博客文章
@api.route('/user/<int:id>/likes/')
def get_user_likes(id):
    user = User.query.get_or_404(id)
    if g.current_user != user or not g.current_user.can(Permission.ADMIN):
        return forbidden('Insufficient permission')
    # 分页
    page = request.args.get('page', 1, type=int)
    likes = user.likes.all()
    pagination = Post.query.filter(Post.id.in_([like.post_id for like in likes])).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_likes', page=page - 1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_likes', page=page + 1)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev_url': prev,
        'next_url': next,
        'count': pagination.total
    })