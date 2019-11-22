from . import user_page
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import User


@user_page.route('/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    # 当试图进入他人的个人主页时，重定向到首页
    if current_user.id != user.id:
        flash("不可以偷看别人的主页哦~")
        return redirect(url_for('main.index'))
    return render_template('user/user_page.html', user=user)
