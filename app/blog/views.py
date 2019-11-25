from . import blog
from app import db
from ..models import Post, Permission, Category
from flask import render_template, abort, flash, redirect, url_for
from flask_login import current_user, login_required
from .forms import PostEditForm

# 博客地址
@blog.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('blog/post.html', post=post)

# 编辑博客
@blog.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostEditForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.category = Category.query.get(form.category.data)
        post.summary = form.summary.data
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('博客已修改成功')
        return redirect(url_for('.post', id=post.id))
    form.title.data = post.title
    form.category.data = post.category_id
    form.summary.data = post.summary
    form.body.data = post.body
    return render_template("blog/edit_post.html", form=form, post=post)
