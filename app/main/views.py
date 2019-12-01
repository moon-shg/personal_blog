from flask import render_template, redirect, url_for, request, current_app, flash
from . import main
from flask_login import current_user
from ..models import User, Role, Permission, Post, Category


# 主页面
@main.route('/', methods=['GET'])
def index():
    # post 分页
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('main/index.html', posts=posts, pagination=pagination)

# 搜索
@main.route('/search', methods=['POST'])
def search():
    if not request.form['search']:
        flash("请输入要搜索的内容", 'error')
        return redirect(url_for('main.index'))
    return redirect(url_for('main.search_results', search_words=request.form['search']))


# 搜索结果
@main.route('/search_results/<search_words>')
def search_results(search_words):
    results_counts = Post.query.whoosh_search(search_words).count()
    # 对搜索结果进行分页
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.whoosh_search(search_words).order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['SEARCH_RESULTS_PER_PAGE'], error_out=False)
    results = pagination.items
    flash(f'共有{ results_counts }条结果，当前显示第{ page }页结果', 'success')
    return render_template('main/search_results.html', search_words=search_words, posts=results, pagination=pagination)