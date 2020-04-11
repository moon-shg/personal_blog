from . import auth
from flask import render_template, request, redirect, url_for, flash
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, ResetPasswordRequestForm, ResetPasswordForm
from ..models import User
from .. import db
from flask_login import login_user, login_required, logout_user, current_user
from ..email import send_email
from datetime import timedelta


# 登录
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data, duration=timedelta(days=1))
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
                flash('欢迎回来！', 'success')
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
            email=form.email.data.lower(),
            password=form.password_1.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, "邮箱验证", 'auth/email/confirm', user=user, token=token)
        flash('一封验证邮件已发送至您的邮箱，请点击其中的验证链接完成注册！')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


# 验证邮箱
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('邮箱验证成功！')
    else:
        flash("验证链接已失效")
    return redirect(url_for('main.index'))


# 修改密码
@auth.route('/change-password/', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.verify_password(form.old_psd.data):
            flash('您输入的旧密码不正确！')
            return redirect(url_for('auth.change_password'))
        else:
            current_user.password = form.new_psd1.data
            db.session.add(current_user)
            db.session.commit()
            flash('密码修改成功！')
            return redirect(url_for('main.index'))
    return render_template('auth/change_password.html', form=form)


# 重置密码请求
@auth.route('/reset-password', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    render_type = 'reset_password_request'  # 用于控制 reset_password.html 渲染样式的变量
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None:
            token = user.generate_reset_password_token()
            send_email(user.email, "重置密码", 'auth/email/reset_password', token=token, user=user)
            flash("一封包含重置密码连接的邮件已发送至您的邮箱，请注意查收")
        else:
            flash("该邮箱并没有注册，请确认输入的邮箱")
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form, render_type=render_type)


# 重置密码页面
@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    render_type = 'reset_password'  # 用于控制 reset_password.html 渲染样式的变量
    if form.validate_on_submit():
        if User.reset_password(token, form.new_psd1.data):
            db.session.commit()
            flash('密码已重置！')
            return redirect(url_for('auth.login'))
        else:
            flash('')
    return render_template('auth/reset_password.html', form=form, render_type=render_type)


# 更新已登录用户的 last_seen 属性
@auth.before_app_request   # 使得程序会在每次请求前执行
def before_request():
    if current_user.is_authenticated:
        current_user.refresh_last_seen()
