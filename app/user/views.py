from . import user_page
import os
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from flask_uploads import UploadNotAllowed
from ..models import User, Permission, Role, Comment
from .forms import EditProfileForm, EditProfileAdminForm
from app import db, avatars
from ..decorators import admin_required

# 个人主页
@user_page.route('/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    # 当试图进入他人的个人主页时，重定向到首页
    if not current_user.can(Permission.ADMIN) and current_user.id != user.id:
        flash("不可以偷看别人的主页哦~")
        return redirect(url_for('main.index'))
    return render_template('user/user_page.html', user=user)

# 编辑个人资料
@user_page.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    user = current_user._get_current_object()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.gender = form.gender.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('资料已更新！')
        return redirect(url_for('user_page.user', username=current_user.username))
    form.name.data = current_user.name if current_user.name else ''
    form.gender.data = current_user.gender
    form.location.data = current_user.location if current_user.location is not None else ''
    form.about_me.data = current_user.about_me if current_user.about_me is not None else ''
    return render_template('user/edit_profile.html', form=form, user=user)

# 编辑个人资料（管理员）
@user_page.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.gender = form.gender.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('资料已更新！')
        return redirect(url_for('.user', username=user.username))
    form.username.data = user.username
    form.email.data = user.email
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.gender.data = user.gender
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('user/edit_profile.html', form=form, user=user)


# 上传头像页面
@user_page.route('/upload-avatar', methods=['GET', 'POST'])
@login_required
def upload_avatar():
    user = current_user._get_current_object()
    if request.method == 'POST' and 'avatar' in request.files:
        try:
            filename = avatars.save(request.files['avatar'])
        except UploadNotAllowed:
            flash('请选择要上传的文件！')
        else:
            user.avatar = url_for('static', filename='img/upload/'+filename)
            db.session.add(user)
            db.session.commit()
            flash('头像已更新')
            return redirect(url_for('user_page.user', username=user.username))
    return render_template('user/upload_avatar.html', user=user)

# 管理个人评论
@user_page.route('/my-comments')
@login_required
def my_comments():
    user = current_user._get_current_object()
    page = request.args.get('page', 1, type=int)
    pagination = user.comments.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=5, error_out=False)
    comments = pagination.items
    return render_template('user/my_comments.html', user=user, page=page, pagination=pagination, comments=comments)
