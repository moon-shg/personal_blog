from . import user_page
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import User, Permission
from .forms import EditProfileForm
from app import db


@user_page.route('/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    # 当试图进入他人的个人主页时，重定向到首页
    if not current_user.can(Permission.ADMIN) and current_user.id != user.id:
        flash("不可以偷看别人的主页哦~")
        return redirect(url_for('main.index'))
    return render_template('user/user_page.html', user=user)


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
    form.gender.data = '男' if current_user.gender else '女'
    form.location.data = current_user.location if current_user.location is not None else ''
    form.about_me.data = current_user.about_me if current_user.about_me is not None else ''
    return render_template('user/edit_profile.html', form=form, user=user)
