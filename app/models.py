from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


# 用户组
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return f'<用户组：{self.name}>'


# 用户
# 通过添加父类UserMixin,来继承Flask_login的一些属性和方法（如：is_authenticated, is_active, is_anonymous 和 get_id()）
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    # 将密码设置为只写属性
    @property
    def password(self):
        raise AttributeError('password is not readalbe attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 验证密码
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<用户名：{self.username}>'


# Flask-login 加载用户
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
