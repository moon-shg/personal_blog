from . import blog
from app import db, post_img
from ..models import Post, Permission, Category, Comment
from flask import render_template, abort, flash, redirect, url_for, request, jsonify, send_from_directory, current_app
from flask_login import current_user, login_required
from .forms import PostEditForm, CommentForm, CommentEditForm, LikePostForm, DislikePostForm, PostForm
from app.decorators import permission_require
from flask_uploads import UploadNotAllowed
from flask_ckeditor import upload_success, upload_fail
import os
from sqlalchemy import extract


# 处理文章头图
def save_post_img():
    if request.method == 'POST' and 'image' in request.files:
        try:
            filename = post_img.save(request.files['image'])
        except UploadNotAllowed:
            pass
        else:
            post.image = url_for("static", filename='img/upload/post_img/' + filename)


# 博客地址
@blog.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    form = CommentForm()  # 用于发表评论的表单
    form2 = CommentEditForm()  # 用于修改评论的表单
    form3 = LikePostForm()  # 用于收藏文章
    form4 = DislikePostForm()  # 用于取消收藏
    type_flag = 'CommentForm'
    post = Post.query.get_or_404(id)
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.timestamp).all()
    user = current_user._get_current_object()
    # 打开后浏览数+1
    post.views += 1
    db.session.add(post)
    db.session.commit()
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
    # 收藏文章
    if form3.validate_on_submit() and form3.submit_like_post.data:
        user.like(post)
        db.session.commit()
        flash('已收藏文章！', 'success')
        return redirect(url_for('blog.post', id=post.id))
    # 取消收藏
    if form4.validate_on_submit() and form4.submit_dislike_post.data:
        user.dislike(post)
        db.session.commit()
        flash('已取消收藏！')
        return redirect(url_for('blog.post', id=post.id))
    return render_template('blog/post.html', post=post, comments=comments, form=form,
                           form2=form2, form3=form3, form4=form4, type_flag=type_flag)


# 发布博客
@blog.route('/new-post', methods=['GET', 'POST'])
@login_required
def new_post():
    if not current_user.can(Permission.ADMIN):
        abort(403)
    post = Post()
    form = PostForm()
    # 处理文章头图
    save_post_img()
    # 处理二级表单
    if request.method == 'POST' and not form.submit.data:
        data = request.get_json()
        name = data['name']
        category = Category.query.filter_by(name=name).first()
        sub_categories = {category.id: category.name for category in
                          Category.query.filter_by(parent_id=category.id).all()}
        return jsonify(sub_categories)
    if form.validate_on_submit():
        post.author_id = current_user.id
        post.title = form.title.data
        if form.sub_category.data:
            post.category = Category.query.get(form.sub_category.data)
        else:
            post.category = Category.query.get(form.category.data)
        post.summary = form.summary.data
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('博客发表')
        return redirect(url_for('.post', id=post.id))
    return render_template("blog/new_post.html", form=form)


# 编辑博客
@blog.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostEditForm()
    # 处理文章头图
    save_post_img()
    # 处理二级表单
    if request.method == 'POST' and not form.submit.data:
        data = request.get_json()
        name = data['name']
        category = Category.query.filter_by(name=name).first()
        sub_categories = {category.id: category.name for category in
                          Category.query.filter_by(parent_id=category.id).all()}
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


# 博客分类页面
@blog.route('/post/<category_name>')
def category_posts(category_name):
    category = Category.query.filter_by(name=category_name).first_or_404()
    page = request.args.get('page', 1, type=int)
    sub_categories = Category.query.filter_by(parent_id=category.id).all()  # 查询二级分类
    categories_list = [sub_category.id for sub_category in sub_categories]  # 二级子分类id列表
    categories_list.append(category.id)  # 分类列表中添加自己(一级分类)
    # 一级分类 并且有子分类
    if not category.parent_id and sub_categories:
        pagination = Post.query.filter(
            Post.category_id.in_(categories_list)).order_by(
            Post.timestamp.desc()).paginate(
            page, per_page=9, error_out=False)
    # 一级分类 但没有子分类 ； 二级分类
    else:
        pagination = Post.query.filter_by(category_id=category.id).order_by(Post.timestamp.desc()).paginate(
            page, per_page=9, error_out=False)
    posts = pagination.items
    no_post_flag = False
    if pagination.total == 0:
        flash('抱歉，该分类下暂时没有文章。', 'warning')
        no_post_flag = True
    return render_template('blog/category_post.html',
                           category=category, posts=posts, page=page, pagination=pagination, no_post_flag=no_post_flag)


# 博客时间归档页面(月)
@blog.route('/<int:year>/<int:month>')
def archive_month(year, month):
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter(extract('year', Post.timestamp) == year,
                                   extract('month', Post.timestamp) == month
                                   ).order_by(Post.timestamp.desc()).paginate(
        page, per_page=9, error_out=False)
    posts = pagination.items
    return render_template('blog/archives_month.html', posts=posts, page=page, pagination=pagination, year=year, month=month)


# 博客时间归档页面(年)
@blog.route('/<int:year>')
def archive_year(year):
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter(extract('year', Post.timestamp) == year).order_by(Post.timestamp.desc()).paginate(
        page, per_page=9, error_out=False)
    posts = pagination.items
    return render_template('blog/archives_year.html', posts=posts, page=page, pagination=pagination, year=year)


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


# 文章内图片
@blog.route('/files/<path:filename>')
def uploaded_files(filename):
    path = '/static/img/upload/post_pic'
    return send_from_directory(path, filename)


@blog.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('upload')  # 获取上传的文件
    # todo: validations here
    extension = f.filename.split('.')[1].lower()
    if extension not in tuple('jpg jpe jpeg png gif svg bmp'.split()):
        return upload_fail(message='只能上传图片！')
    f.save(os.path.join('/static/img/upload/post_pic', f.filename))
    url = url_for('blog.uploaded_files', filename=f.filename)
    return upload_success(url=url)
