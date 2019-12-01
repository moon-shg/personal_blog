from . import api
from app.models import Post, Permission, Category
from flask import jsonify, request, g, url_for
from .decorators import permission_required
from app import db
from flask_whooshalchemyplus import index_one_model
from .errors import forbidden


@api.route('/posts/')
def get_posts():
    posts = Post.query.all()
    return jsonify({'posts': [post.to_json() for post in posts]})


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
    index_one_model(Post)
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
        category_id = Category.query.filter_by(name=json_post.get('category')).first().id
    post.category_id = category_id
    db.session.add(post)
    db.session.commit()
    index_one_model(Post)
    return jsonify(post.to_json())
