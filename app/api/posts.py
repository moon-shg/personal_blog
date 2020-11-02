from . import api
from app.models import Post, Permission, Category, Comment
from flask import jsonify, request, g, url_for, current_app
from .decorators import permission_required
from app import db
# from flask_whooshalchemyplus import index_one_model
from .errors import forbidden


@api.route('/posts/')
def get_posts():
    # 分页
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page - 1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=page + 1)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev_url': prev,
        'next_url': next,
        'count': pagination.total
    })


# 获取某篇文章
@api.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())


# 创建博客文章
@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    # index_one_model(Post)
    return jsonify(post.to_json()), 201, {'Location': url_for('api.get_post', id=post.id)}


# 修改博客文章
@api.route('/posts/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and not g.current_user.can(Permission.ADMIN):
        return forbidden('Insufficient permission')
    post.title = request.json.get('title', post.title)
    post.summary = request.json.get('summary', post.summary)
    post.body = request.json.get('body', post.body)
    category = Category.query.filter_by(name=request.json.get('category')).first()
    # 如果没有设置分类，则设置为默认分类
    if category is None:
        category_id = Category.query.filter_by(default=True).first().id
    else:
        category_id = Category.query.filter_by(name=request.json.get('category')).first().id
    post.category_id = category_id
    db.session.add(post)
    db.session.commit()
    # index_one_model(Post)
    return jsonify(post.to_json())


# 获取文章评论
@api.route('/posts/<int:id>/comments/')
def get_post_comments(id):
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.filter_by(post_id=id, disable=False).paginate(page, per_page=10, error_out=False)
    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_post_comments', page=page - 1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_post_comments', page=page + 1)
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'prev_url': prev,
        'next_url': next,
        'count': pagination.total
    })


# 发表文章评论
@api.route('/posts/<int:id>/comments/', methods=['POST'])
@permission_required(Permission.COMMENT)
def new_comment(id):
    comment = Comment.from_json(request.json)
    comment.author = g.current_user
    comment.post = Post.query.get_or_404(id)
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json()), 201, {'Location': url_for('api.get_comment', id=comment.id)}
