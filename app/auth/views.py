from . import auth
from flask import render_template, request, redirect, url_for, flash
from .forms import LoginForm, RegistrationForm
from ..models import User
from .. import db
from flask_login import login_user, login_required, logout_user


# 登录
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startwith('/'):
                next = url_for('main.index')
                flash('欢迎回来！')
            return redirect(next)
        flash('邮箱或密码错误！')
    return render_template('auth/login.html', form=form)


# 登出
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录，欢迎下次再来~')
    return redirect(url_for('main.index'))


# 注册
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password_1.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功！')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)
