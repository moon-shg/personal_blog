from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from . import api
from ..models import User
from .errors import unauthorized, forbidden

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password):
    # 没有 email 或令牌 token
    if email_or_token == '':
        return False
    # 使用令牌 token 登录
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True  # token_used 属性 用来区分用户的身份验证方式
        return g.current_user is not None
    # 使用邮箱密码登录
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@api.route('/tokens/', methods=['POST'])
def get_token():
    # 如果是匿名用户或者用户已经用 token 登录了(确保这个路由只能由邮箱密码登录的用户访问)，则返回403
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    expiration = 3600
    token = g.current_user.generate_auth_token(expiration=expiration)
    return jsonify({'token': token, 'expiration': expiration})


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


# 访问资源前进行身份验证
@api.before_request
@auth.login_required
def before_request():
    pass
