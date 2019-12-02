from . import api
from flask import request, current_app, url_for, jsonify
from app.models import Category

# 获取某个分类下的所有文章
@api.route('/category/<name>/posts/')
def get_category_posts(name):
    category = Category.query.filter_by(name=name).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = category.posts.paginate(page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_category_posts', page=page - 1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_category_posts', page=page + 1)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev_url': prev,
        'next_url': next,
        'count': pagination.total
    })
