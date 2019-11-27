from . import blog
from app import db
from ..models import Post, Permission, Category, Comment
from flask import render_template, abort, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from .forms import PostEditForm, CommentForm, CommentEditForm
from app.decorators import permission_require


# 博客地址
@blog.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    form = CommentForm()  # 用于发表评论的表单
    form2 = CommentEditForm()  # 用于修改评论的表单
    type_flag = 'CommentForm'
    post = Post.query.get_or_404(id)
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.timestamp).all()
    # 文章评论
    if form.validate_on_submit() and form.submit_comment.data:
        comment = Comment(
            body=form.body.data,
            post=post,
            author=current_user._get_current_object(),
            parent=Comment.query.get(form.parent.data)
        )
        db.session.add(comment)
        db.session.commit()
        flash("您的评论已发布！")
        return redirect(url_for('blog.post', id=post.id))
    # 修改评论
    if form2.validate_on_submit() and form2.submit_edit_comment.data:
        comment = Comment.query.get_or_404(form2.id.data)
        comment.body = form2.body.data
        db.session.add(comment)
        db.session.commit()
        flash('已修改评论！')
        return redirect(url_for('blog.post', id=post.id))
    return render_template('blog/post.html', post=post, comments=comments, form=form,
                           form2=form2, type_flag=type_flag)

# 编辑博客
@blog.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostEditForm()
    # 处理二级表单
    if request.method == 'POST' and not form.submit.data:
        data = request.get_json()
        name = data['name']
        category = Category.query.filter_by(name=name).first()
        sub_categories = {category.id: category.name for category in Category.query.filter_by(parent_id=category.id).all()}
        return jsonify(sub_categories)
    if form.validate_on_submit():
        post.title = form.title.data
        if form.sub_category.data:
            post.category = Category.query.get(form.sub_category.data)
        else:
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




# 管理评论
@blog.route('/moderate/<int:id>')
@login_required
@permission_require(Permission.MODERATE)
def moderate(id):
    page = request.args.get('page', 1, type=int)
    post = Post.query.get_or_404(id)
    pagination = Comment.query.filter_by(post_id=id).order_by(Comment.timestamp.desc()).paginate(
        page, per_page=10, error_out=False)
    comments = pagination.items
    return render_template('blog/comment_moderate.html', post=post, comments=comments, pagination=pagination, page=page)

# 解除屏蔽
@blog.route('/moderate/enable/<int:id>')
@login_required
@permission_require(Permission.MODERATE)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disable = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('blog.moderate', id=comment.post_id, page=request.args.get('page', 1, type=int)))


# 屏蔽评论
@blog.route('/moderate/disable/<int:id>')
@login_required
@permission_require(Permission.MODERATE)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disable = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('blog.moderate', id=comment.post_id, page=request.args.get('page', 1, type=int)))